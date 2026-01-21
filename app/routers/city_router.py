from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
from app.logger import setup_logger
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from app.database import database_utils
from app.utils import app_utils

# ✅ THIS MUST BE NAMED `router`
router = APIRouter(prefix="", tags=["users"])
logger = setup_logger()

templates = Jinja2Templates(directory="templates")



@router.post("/search/city", response_class=JSONResponse)
async def get_cities(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    session_token = body.get("session_token")
    prefix = body.get("prefix")

    validate_session = app_utils.verify_session(session_token, user_id, database_utils, logger)
    if not validate_session:
        logger.info("Invalid or expired session")
        return app_utils.failure_response(202, "Invalid or expired Session token")

    if len(prefix) < 3:
        return app_utils.failure_response(400, "Prefix must be at least 3 characters long")
    city_names = database_utils.get_city_names_by_prefix(prefix, logger)
    response= {
        "cities": city_names
    }
    return JSONResponse(content=app_utils.sucess_response(response))

