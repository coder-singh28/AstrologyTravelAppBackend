from datetime import datetime, time
import uuid
from app.aes_encrypt import encrypt, decrypt_string


class app_utils:
    """Application utility functions"""

    @staticmethod
    def get_day(travel_datetime: str) -> str:
        """Get day name from ISO format datetime string"""
        dt = datetime.fromisoformat(travel_datetime)
        return dt.strftime("%A")  # Monday, Tuesday...

    @staticmethod
    def get_hora_index(travel_datetime: str, sunrise_hour: int = 6) -> int:
        """Calculate hora index from travel time and sunrise hour"""
        dt = datetime.fromisoformat(travel_datetime)
        sunrise = dt.replace(hour=sunrise_hour, minute=0, second=0)
        diff_hours = (dt - sunrise).total_seconds() / 3600
        return int(diff_hours) % 24

    @staticmethod
    def create_session() -> str:
        """Generate unique session token"""
        return str(uuid.uuid4())

    @staticmethod
    def success_response(response, status_code: str = "202") -> dict:
        """Format success response"""
        return {
            "status": "success",
            "status_code": status_code,
            "response": encrypt(response)
            # "response": (response)
        }

    @staticmethod
    def sucess_response(response, status_code: str = "202") -> dict:
        """Legacy method name - use success_response instead"""
        return app_utils.success_response(response, status_code)

    @staticmethod
    def failure_response(status_code: int, message: str) -> dict:
        """Format failure response"""
        return {
            "status": "failure",
            "status_code": str(status_code),
            "response": message
        }

    @staticmethod
    def verify_session(session_token: str, user_id: int, database_utils, logger, request) -> bool:
        """Verify if session is valid and not expired using parameterized query"""
        logger.info(f"Verifying session for user_id: {user_id} with token: {session_token}")

        cache_session = request.session.get(f"session_details_{user_id}")
        if cache_session == session_token:
            logger.info(f"Session valid for user_id: {user_id} :: found in cache")
            return True
        else:
            logger.info(f"No valid session in cache for user_id: {user_id}, checking database")
            query = "SELECT * FROM session_details WHERE session_token = %s AND user_id = %s AND expires_at > NOW()"
            try:
                result = database_utils.performeSelectStatement(query, (session_token, user_id), logger)
                is_valid = bool(result)
                if is_valid:
                    request.session[f"session_details_{user_id}"] = session_token
                    logger.info(f"Session valid for user_id: {user_id} found in database and saved cached")
                return is_valid
            except Exception as e:
                logger.error(f"Session verification error: {str(e)}")
                return False

    @staticmethod
    def get_user_details(user_id, database_utils, logger, request, session_token):
        logger.info(f"Retrieving details for user_id: {user_id}")
        user_data = request.session.get(f"user_details_{user_id}")

        if user_data and user_data.get("user_id") == user_id:
            logger.info(f"User details found in session for user_id: {user_id} :: data : {user_data}")
            return (user_data["user_id"], user_data["email"], user_data["full_name"], user_data["mobile_no"],
                    user_data["dob"], user_data["tob"], user_data["birth_place"])
        else:
            logger.info(f"No user details in session for user_id: {user_id}, querying database")
            query = "SELECT id, email, full_name, mobile_no, dob, tob, birth_place FROM users_details WHERE id = %s"
            result = database_utils.performeSelectStatement(query, (user_id,), logger)
            if result:
                user_data = {
                    "user_id": result[0][0],
                    "email": result[0][1],
                    "full_name": result[0][2],
                    "mobile_no": result[0][3],
                    "dob": result[0][4],
                    "tob": result[0][5],
                    "birth_place": result[0][6],
                    "session_token": session_token,
                }
                request.session[f"user_details_{user_id}"] = user_data
                logger.info(f"User details retrieved from database and saved in session for user_id: {user_id} :: data : {user_data}")
            return result[0] if result else None

    @staticmethod
    def update_user_details(user_id: int, full_name: str, mobile_no: str, dob: str, tob: str, birth_place: str,
                            database_utils, logger, request, session_token) -> bool:
        keys = [f"user_details_{user_id}"]
        for key in keys:
            request.session.pop(key, None)
            logger.info(f"Cleared session cache for key: {key} after profile update for user_id: {user_id}")

        query = "UPDATE users_details SET full_name = %s, mobile_no = %s, dob = %s, tob = %s, birth_place = %s WHERE id = %s"
        try:
            database_utils.performInsertUpdateDelete(query, (full_name, mobile_no, dob, tob, birth_place, user_id),
                                                     logger)
            logger.info(f"User details updated in database for user_id: {user_id}")
            # app_utils.get_user_details(user_id, database_utils, logger,request,session_token)  # Refresh session cache with updated details
            return True
        except Exception as e:
            logger.error(f"Error updating user details for user_id {user_id}: {str(e)}")
            return False
