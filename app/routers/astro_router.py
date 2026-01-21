from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.logger import setup_logger
from app.database import database_utils
from app.utils import app_utils
from app.direction import get_direction, predict_travel_utils
from datetime import datetime
from app.services import tithi_service

# ✅ THIS MUST BE NAMED `router`
router = APIRouter(prefix="/astro", tags=["Astro"])
logger = setup_logger()

@router.post("/get_lat_long", response_class=JSONResponse)
async def get_lat_long(request: Request):
    """
    Get latitude and longitude for a given place.
    Requires: user_id, session_token, place
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        return app_utils.failure_response(400, f"Invalid JSON format: {str(e)}")
    
    user_id = body.get("user_id")
    session_token = body.get("session_token")
    place = body.get("place")
    logger.info(f"Received request for lat/long of place: {place} by user_id: {user_id}")
    
    # Validate session FIRST before processing
    validate_session = app_utils.verify_session(session_token, user_id, database_utils, logger)
    if not validate_session:
        logger.info("Invalid or expired session")
        return app_utils.failure_response(202, "Invalid or expired Session token")
    
    # Only process if session is valid
    logger.info(f"Valid session for user_id: {user_id}")
    latlong = get_direction.get_lat_lon(place)
    logger.info(f"Lat/Long for place {place}: {latlong}")
    
    response = {
        "user_id": user_id,
        "session_token": session_token,
        "lat": latlong[0],
        "long": latlong[1],
    }
    return JSONResponse(content=app_utils.sucess_response(response))

@router.post("/predict_travel", response_class=JSONResponse)
async def fn_predict_travel(request: Request):
    """
    Predict travel timing and auspiciousness for a journey.
    Requires: user_id, session_token, source, destination, travel_date
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        return app_utils.failure_response(400, f"Invalid JSON format: {str(e)}")
    
    user_id = body.get("user_id")
    session_token = body.get("session_token")
    source = body.get("source")
    destination = body.get("destination")
    travel_date = body.get("travel_date")
    logger.info(f"Received travel prediction request from {source} to {destination} on {travel_date} by user_id: {user_id}")

    # Validate session FIRST before processing
    validate_session = app_utils.verify_session(session_token, user_id, database_utils, logger)
    if not validate_session:
        logger.info("Invalid or expired session")
        return app_utils.failure_response(202, "Invalid or expired Session token")
    
    logger.info(f"Valid session for user_id: {user_id}")
    
    # Use parameterized query to prevent SQL injection
    query = "SELECT id, email, full_name, mobile_no, dob, tob, birth_place FROM users_details WHERE id = %s"
    result = database_utils.performeSelectStatement(query, (user_id,), logger)
    
    if not result:
        logger.warning(f"User not found: {user_id}")
        return app_utils.failure_response(404, "User details not found")
    
    # Extract user details from first result
    user_data = result[0]
    user_id, email, full_name, mobile_no, dob, tob, birth_place = user_data
    logger.info(f"User details - ID: {user_id}, Email: {email}, Name: {full_name}, Mobile: {mobile_no}, DOB: {dob}, TOB: {tob}, Birth Place: {birth_place}")
    
    # Get geospatial information
    source_latlong = get_direction.get_lat_lon(source)
    destination_latlong = get_direction.get_lat_lon(destination)
    direction_info = get_direction.get_direction_info(source, destination)
    
    # Convert travel_date to datetime object
    travel_dt = datetime.strptime(travel_date, "%d-%m-%Y").replace(hour=7, minute=0)
    
    # Predict travel based on astrological calculations
    result = predict_travel_utils.predict_travel(
        travel_dt=travel_dt,
        lat=source_latlong[0],
        lon=source_latlong[1],
        direction=direction_info["direction"],
        dob=dob,
        tob=tob,
        pob_lat=get_direction.get_lat_lon(birth_place)[0],
        pob_lon=get_direction.get_lat_lon(birth_place)[1],
    )
    
    return JSONResponse(content=app_utils.sucess_response(result))

@router.post("/analyse_journey", response_class=JSONResponse)
async def fn_analyse_journey(request: Request):
    """
    Analyze astrological aspects of a journey based on tithi and direction.
    Requires: user_id, session_token, source, destination, travel_date, travel_time
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        return app_utils.failure_response(400, f"Invalid JSON format: {str(e)}")
    
    user_id = body.get("user_id")
    session_token = body.get("session_token")
    source = body.get("source")
    destination = body.get("destination")
    travel_date = body.get("travel_date")
    travel_time = body.get("travel_time")

    # Validate session FIRST before processing
    validate_session = app_utils.verify_session(session_token, user_id, database_utils, logger)
    if not validate_session:
        logger.info("Invalid or expired session")
        return app_utils.failure_response(202, "Invalid or expired Session token")
    
    logger.info(f"Valid session for user_id: {user_id}")
    
    # Get astrological information
    tithi = tithi_service.get_tithi(travel_date)
    day = tithi_service.get_day_and_date(travel_date)[0]
    direction_info = get_direction.get_direction_info(source, destination)
    
    response = {
        "user_id": user_id,
        "session_token": session_token,
        "source": source,
        "destination": destination,
        "travel_date": travel_date,
        "travel_time": travel_time,
        "tithi": tithi,
        "day": day,
        "direction": direction_info["direction"],
    }
    return JSONResponse(content=app_utils.sucess_response(response))
