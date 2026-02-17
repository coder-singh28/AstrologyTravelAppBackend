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
            # "response": encrypt(response)
            "response": (response)
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
    def verify_session(session_token: str, user_id: str, database_utils, logger) -> bool:
        """Verify if session is valid and not expired using parameterized query"""
        query = "SELECT * FROM session_details WHERE session_token = %s AND user_id = %s AND expires_at > NOW()"
        try:
            result = database_utils.performeSelectStatement(query, (session_token, user_id), logger)
            is_valid = bool(result)
            logger.info(f"Session validation for user {user_id}: {'Valid' if is_valid else 'Invalid'}")
            return is_valid
        except Exception as e:
            logger.error(f"Session verification error: {str(e)}")
            return False
