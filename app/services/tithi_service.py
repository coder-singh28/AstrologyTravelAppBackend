"""
Tithi (Lunar Day) Service Module
Calculates lunar day (tithi) based on moon phase cycles using a known reference date.
Tithi: One of 30 lunar days in the lunar month, each approximately 12° of moon-sun angular distance.
"""

from datetime import datetime
import math

# 30 lunar days in order (Shukla - waxing phase, Krishna - waning phase)
TITHI_LIST = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada (Krishna)", "Dwitiya (Krishna)", "Tritiya (Krishna)",
    "Chaturthi (Krishna)", "Panchami (Krishna)", "Shashthi (Krishna)",
    "Saptami (Krishna)", "Ashtami (Krishna)", "Navami (Krishna)",
    "Dashami (Krishna)", "Ekadashi (Krishna)", "Dwadashi (Krishna)",
    "Trayodashi (Krishna)", "Chaturdashi (Krishna)", "Amavasya"
]

# Reference point: Known new moon (Amavasya) date and time
REFERENCE_NEW_MOON = datetime(2000, 1, 6, 18, 14)

# Synodic month: Time between successive new moons (lunar cycle)
SYNODIC_MONTH = 29.53058867  # days


def get_day_and_date(travel_date: str) -> tuple:
    """
    Parse travel date and return weekday name and formatted date.
    
    Args:
        travel_date (str): Date in DD-MM-YYYY format
    
    Returns:
        tuple: (weekday: str, date_string: str)
               e.g., ("Monday", "25 December 2024")
    """
    date_obj = datetime.strptime(travel_date, "%d-%m-%Y")
    return date_obj.strftime("%A"), date_obj.strftime("%d %B %Y")


def get_tithi(date_str: str) -> str:
    """
    Calculate tithi (lunar day) for a given date.
    
    Based on lunar age (days since last new moon) divided into 30 equal parts.
    Calculation: 
    1. Calculate days elapsed since reference new moon
    2. Find position in synodic month (0-29.53)
    3. Divide into 30 tithis
    
    Args:
        date_str (str): Date in DD-MM-YYYY format
    
    Returns:
        str: Tithi name (e.g., "Pratipada", "Purnima", "Amavasya")
    """
    date = datetime.strptime(date_str, "%d-%m-%Y")
    
    # Calculate days elapsed since reference new moon
    days_elapsed = (date - REFERENCE_NEW_MOON).total_seconds() / 86400
    
    # Find position in current lunar cycle (0 to synodic_month)
    lunar_age = days_elapsed % SYNODIC_MONTH
    
    # Determine tithi (0-29)
    tithi_index = int(lunar_age // (SYNODIC_MONTH / 30))
    tithi_index = tithi_index % len(TITHI_LIST)  # Ensure within bounds
    
    return TITHI_LIST[tithi_index]


def get_auspicious_time(day: str) -> str:
    """
    Determine auspicious travel time windows based on weekday.
    
    Note: This is a simplified/sample implementation.
    Full Muhurat analysis requires:
    - Hora (hourly divisions)
    - Tithi
    - Nakshatra
    - Yoga
    - Karana
    
    Args:
        day (str): Weekday name (e.g., "Monday", "Tuesday")
    
    Returns:
        str: Auspicious time window or avoidance recommendation
    """
    # Simplified logic - full Muhurat needs ephemeris calculations
    if day in ["Tuesday", "Saturday"]:
        return "Avoid travel (Ashubh)"
    
    # Default auspicious window
    return "06:00 AM – 10:30 AM"
