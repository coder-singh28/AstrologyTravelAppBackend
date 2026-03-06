from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz

DAY_ORDER   = ["Udveg","Chal","Labh","Amrit","Kaal","Shubh","Rog","Udveg"]
NIGHT_ORDER = ["Shubh","Amrit","Chal","Rog","Kaal","Labh","Udveg","Shubh"]

def get_chaughadiya_json(city, country, latitude, longitude, date=None):

    timezone_str = "Asia/Kolkata"
    tz = pytz.timezone(timezone_str)

    loc = LocationInfo(city, country, timezone_str, latitude, longitude)

    if date:
        today = datetime.strptime(date, "%Y-%m-%d").date()
    else:
        today = datetime.now(tz).date()

    s = sun(loc.observer, date=today, tzinfo=tz)
    sunrise = s["sunrise"]
    sunset  = s["sunset"]

    next_sun = sun(loc.observer, date=today + timedelta(days=1), tzinfo=tz)
    next_sunrise = next_sun["sunrise"]

    day_duration   = (sunset - sunrise) / 8
    night_duration = (next_sunrise - sunset) / 8

    result = {
        "city": city,
        "date": str(today),
        "sunrise": sunrise.strftime("%H:%M:%S"),
        "sunset": sunset.strftime("%H:%M:%S"),
        "day_chaughadiya": [],
        "night_chaughadiya": []
    }

    # Day slots
    current = sunrise
    for name in DAY_ORDER:
        start = current
        end = current + day_duration
        result["day_chaughadiya"].append({
            "name": name,
            "start": start.strftime("%H:%M:%S"),
            "end": end.strftime("%H:%M:%S")
        })
        current = end

    # Night slots
    current = sunset
    for name in NIGHT_ORDER:
        start = current
        end = current + night_duration
        result["night_chaughadiya"].append({
            "name": name,
            "start": start.strftime("%H:%M:%S"),
            "end": end.strftime("%H:%M:%S")
        })
        current = end

    return result


# Example usage
if __name__ == "__main__":
    data = get_chaughadiya_json(
        city="Jaipur",
        country="India",
        latitude=26.9124,
        longitude=75.7873
    )

    import json
    print(json.dumps(data, indent=4))
