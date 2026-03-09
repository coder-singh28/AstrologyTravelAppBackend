"""
Authentication Router Module
Handles Google OAuth2 authentication, user management, and session creation.
"""

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
from dotenv import load_dotenv

env = os.getenv("APP_ENV", "dev")
if env == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")

# ✅ THIS MUST BE NAMED `router`
router = APIRouter(prefix="/api", tags=["Authentication"])
logger = setup_logger()

# Hardcoded credentials (TODO: Move to environment variables)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

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
# Google OAuth2 Login
# ----------------------------------------
@router.get("/auth/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth2 login flow.
    Redirects user to Google consent screen.
    """
    redirect_uri = os.getenv("redirect_uri")
    logger.info(f"Initiating Google OAuth2 login, env redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)


# ----------------------------------------
# Google OAuth2 Callback Handler
# ----------------------------------------
@router.get("/auth/callback", name="google_auth_callback")
async def google_auth_callback(request: Request):
    """
    Handle Google OAuth2 callback and establish session.
    Creates or updates user record in database and returns redirect to dashboard.
    """
    logger.info("Handling Google OAuth2 callback")
    try:
        token = await oauth.google.authorize_access_token(request)
        logger.info("Google access token obtained successfully")
        
        user = token.get("userinfo")
        logger.info(f"Google user info retrieved: {user.get('email')}")
        
        if not user:
            logger.error("No user information in OAuth token")
            return JSONResponse({"error": "Authentication failed"}, status_code=400)
        
        # Store user in session for web flow
        request.session["user"] = {
            "google_id": user["sub"],
            "email": user["email"],
            "name": user["name"],
        }
        
        return RedirectResponse(url="/dashboard")
    
    except Exception as e:
        logger.error(f"Google OAuth2 callback error: {str(e)}")
        return JSONResponse({"error": "Authentication failed"}, status_code=400)


# ----------------------------------------
# Dashboard (Authenticated)
# ----------------------------------------
@router.get("/user/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    """
    Serve dashboard for authenticated users.
    Requires active session.
    """
    user = request.session.get("user")
    
    if not user:
        return RedirectResponse(url="/")
    
    logger.info(f"Serving dashboard for user: {user['email']}")
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "user": user,
            "email": user["email"],
            "name": user["name"],
        }
    )


# ----------------------------------------
# Verify Google Token & Create Session
# ----------------------------------------
@router.post("/auth/google/verify-token")
def verify_google_token(data: GoogleAuthRequest):
    """
    Verify Google OAuth2 ID token and authenticate user.
    Creates new user in database if not exists.
    Generates session token for API access.
    
    Returns: user_id, email, full_name, session_token, and other user details
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
