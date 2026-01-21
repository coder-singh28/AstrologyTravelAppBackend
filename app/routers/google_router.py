from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from fastapi.templating import Jinja2Templates
from app.logger import setup_logger
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from app.database import database_utils
from app.utils import app_utils
import os

# ✅ THIS MUST BE NAMED `router`
router = APIRouter(prefix="/google", tags=["Google Auth"])
logger = setup_logger()

# Hardcoded credentials (TODO: Move to environment variables)
GOOGLE_CLIENT_ID = "1096668498798-mdij7sqd1773r4j22irnsv5t1tkcqphg.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

templates = Jinja2Templates(directory="templates")

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Request/Response Models
class GoogleAuthRequest(BaseModel):
    """Pydantic model for Google authentication token verification"""
    token: str

class GoogleUserResponse(BaseModel):
    """Pydantic model for Google user authentication response"""
    email: str
    name: str
    google_id: str


# ----------------------------------------
# Login endpoint
# ----------------------------------------
@router.get("/auth/login-google")
async def login_with_google(request: Request):
    """
    Initiate Google OAuth2 login flow.
    Redirects to Google consent screen.
    """
    redirect_uri = request.url_for("google_callback")
    logger.info(f"Initiating Google OAuth2 login, redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)


# ----------------------------------------
# Google OAuth2 Callback
# ----------------------------------------
@router.get("/auth/callback", name="google_callback")
async def google_callback(request: Request):
    """
    Handle Google OAuth2 callback and create session.
    Creates or updates user record and returns session token.
    """
    logger.info("Handling Google OAuth2 callback")
    try:
        token = await oauth.google.authorize_access_token(request)
        logger.info("Google access token obtained successfully")
        logger.info(f"OAuth Token: {token}")
        logger.info(f"OAuth id_token: {token.get('id_token')}")

        user = token.get("userinfo")
        logger.info(f"Google user info retrieved: {user.get('email')}")
        
        if not user:
            logger.error("No user information in OAuth token")
            return JSONResponse({"error": "Authentication failed"}, status_code=400)
        
        # Store user in session
        request.session["user"] = {
            "google_id": user["sub"],
            "email": user["email"],
            "name": user["name"],
        }
        
        return RedirectResponse(url="/home")
    
    except Exception as e:
        logger.error(f"Google OAuth2 callback error: {str(e)}")
        return JSONResponse({"error": "Authentication failed"}, status_code=400)


# ----------------------------------------
# Token Verification & User Management
# ----------------------------------------
@router.post("/auth/verify")
def verify_google_token(data: GoogleAuthRequest):
    """
    Verify Google OAuth2 token and authenticate user.
    Creates new user if not exists, generates session token.
    Returns: user_id, email, full_name, session_token
    """
    try:
        # Verify Google token signature and validity
        idinfo = id_token.verify_oauth2_token(
            data.token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        # Extra security check for token issuer
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.warning("Invalid token issuer detected")
            raise ValueError("Invalid issuer")
        
        email = idinfo.get("email")
        name = idinfo.get("name")
        
        logger.info(f"Verifying user: {email}")
        
        # Check if user exists in database (using parameterized query)
        query = "SELECT * FROM users_details WHERE email = %s"
        result = database_utils.performeSelectStatement(query, (email,), logger)
        
        # Create new user if not exists
        if not result:
            logger.info(f"New user detected, inserting into database: {email}")
            insert_query = "INSERT INTO users_details (email, full_name) VALUES (%s, %s)"
            database_utils.performInsertUpdateDelete(insert_query, (email, name), logger)
        
        # Retrieve complete user information
        query = "SELECT id, email, full_name, mobile_no, dob, tob, birth_place FROM users_details WHERE email = %s"
        result = database_utils.performeSelectStatement(query, (email,), logger)
        
        if not result:
            logger.error(f"Failed to retrieve user after creation: {email}")
            return app_utils.failure_response(500, "Failed to create user record")
        
        # Extract user data from first result
        user_data = result[0]
        user_id, email, full_name, mobile_no, dob, tob, birth_place = user_data
        logger.info(f"User authenticated - ID: {user_id}, Email: {email}, Name: {full_name}")
        
        # Create session token
        session_token = app_utils.create_session()
        
        # Insert session into database (using parameterized query)
        insert_query = "INSERT INTO session_details (user_id, email, session_token, expires_at) VALUES (%s, %s, %s, NOW() + INTERVAL '1 hour')"
        database_utils.performInsertUpdateDelete(insert_query, (user_id, email, session_token), logger)
        
        logger.info(f"Session created for user: {user_id}")
        
        # Return user data with session token
        response = {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "mobile_no": mobile_no,
            "dob": str(dob),
            "tob": tob,
            "birth_place": birth_place,
            "session_token": session_token,
        }
        return app_utils.sucess_response(response)
    
    except ValueError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return app_utils.failure_response(202, "Invalid or expired Google token")
    except Exception as e:
        logger.error(f"Unexpected error in verify_google_token: {str(e)}")
        return app_utils.failure_response(500, "Internal server error")
