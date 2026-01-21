from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.logger import setup_logger
from app.database import database_utils
from app.utils import app_utils

# ✅ THIS MUST BE NAMED `router`
router = APIRouter(prefix="/users", tags=["Users"])
logger = setup_logger()


@router.post("/details", response_class=JSONResponse)
async def user_details(request: Request):
    """
    Get authenticated user details
    
    JSON body:
        {
            "user_id": 1,
            "session_token": "token_string"
        }
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        return app_utils.failure_response(400, f"Invalid JSON format: {str(e)}")
    
    user_id = body.get("user_id")
    session_token = body.get("session_token")

    # Validate session first
    validate_session = app_utils.verify_session(session_token, user_id, database_utils, logger)
    if not validate_session:
        logger.warning(f"Invalid session for user_id: {user_id}")
        return app_utils.failure_response(202, "Invalid or expired Session token")

    # Query user details using parameterized query
    query = "SELECT id, email, full_name, mobile_no, dob, tob, birth_place FROM users_details WHERE id = %s"
    result = database_utils.performeSelectStatement(query, (user_id,), logger)
    
    if not result:
        logger.warning(f"User not found: {user_id}")
        return app_utils.failure_response(404, "User not found")
    
    row = result[0]
    response = {
        "user_id": row[0],
        "email": row[1],
        "full_name": row[2],
        "mobile_no": row[3],
        "dob": str(row[4]),
        "tob": row[5],
        "birth_place": row[6],
        "session_token": session_token,
    }
    
    logger.info(f"User details retrieved for user_id: {user_id}")
    return JSONResponse(content=app_utils.sucess_response(response))
