"""
Astrological Travel Prediction Module
Calculates auspiciousness of travel based on Vedic astrology principles:
- Tithi (lunar day)
- Nakshatra (lunar mansion)
- Rashi (zodiac sign)
- Karana (half-tithi)
- Bhadra (inauspicious period)
- Panchak (five-day inauspicious period)
- Tara Bala (lunar mansion balance based on birth nakshatra)
"""

import swisseph as swe
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# =================================================
# EPHEMERIS SETUP
# =================================================

swe.set_sid_mode(swe.SIDM_LAHIRI)  # Use Lahiri ayanamsa for sidereal calculations

# Lunar mansions (27 nakshatras)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Zodiac signs (12 rashis)
RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Auspicious nakshatras for travel
GOOD_NAK_YATRA = {
    "Ashwini", "Mrigashira", "Punarvasu", "Pushya",
    "Hasta", "Swati", "Anuradha", "Shravana"
}

# Neutral nakshatras for travel
NEUTRAL_NAK_YATRA = {
    "Rohini", "Uttara Phalguni", "Uttara Ashadha"
}

# Auspicious tithis (lunar days) for travel
GOOD_TITHI = {2, 3, 5, 7, 10, 11, 13}
NEUTRAL_TITHI = {1, 6, 8, 12}

# Disha Shool - inauspicious directions for each weekday
DISHA_SHOOL = {
    "Sunday": "West", "Monday": "East", "Tuesday": "North",
    "Wednesday": "North", "Thursday": "South",
    "Friday": "West", "Saturday": "East"
}

# Panchak types for each weekday
PANCHAK_TYPE = {
    "Sunday": "Mrityu", "Monday": "Agni", "Tuesday": "Raja",
    "Wednesday": "Chora", "Thursday": "Rog",
    "Friday": "Udvega", "Saturday": "Shoka"
}


# =================================================
# TIME CONVERSION & EPHEMERIS HELPERS
# =================================================

def to_utc(dt, lat, lon):
    """
    Convert local datetime to UTC based on coordinates.
    
    Args:
        dt (datetime): Local datetime
        lat (float): Latitude
        lon (float): Longitude
    
    Returns:
        datetime: UTC datetime
    """
    tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lon)
    tz = pytz.timezone(tz_name)
    return tz.localize(dt).astimezone(pytz.utc)


def julian_day(dt_utc):
    """
    Calculate Julian Day Number from UTC datetime.
    
    Args:
        dt_utc (datetime): UTC datetime
    
    Returns:
        float: Julian Day Number for ephemeris calculations
    """
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600
    )


def moon_sun_longitudes(dt_utc):
    """
    Calculate Moon and Sun longitudes in degrees (0-360).
    
    Args:
        dt_utc (datetime): UTC datetime
    
    Returns:
        tuple: (moon_longitude, sun_longitude) in degrees
    """
    jd = julian_day(dt_utc)
    moon = swe.calc_ut(jd, swe.MOON)[0][0] % 360
    sun = swe.calc_ut(jd, swe.SUN)[0][0] % 360
    return moon, sun


# =================================================
# NAKSHATRA & RASHI FROM LONGITUDE
# =================================================

def nakshatra_from_longitude(lon):
    """
    Determine nakshatra (lunar mansion) from moon longitude.
    Each nakshatra spans 13°20' (13.333°).
    
    Args:
        lon (float): Longitude in degrees
    
    Returns:
        str: Nakshatra name
    """
    return NAKSHATRAS[int(lon // (13 + 1 / 3))]


def rashi_from_longitude(lon):
    """
    Determine rashi (zodiac sign) from moon longitude.
    Each rashi spans 30°.
    
    Args:
        lon (float): Longitude in degrees
    
    Returns:
        str: Rashi name
    """
    return RASHIS[int(lon // 30)]


# =================================================
# TITHI, KARANA, BHADRA CALCULATIONS
# =================================================

def tithi_karana(moon, sun):
    """
    Calculate tithi (lunar day) and karana (half-tithi) from moon and sun longitudes.
    Tithi: 30 lunar days based on moon-sun angular distance
    Karana: 60 half-tithis
    
    Args:
        moon (float): Moon longitude in degrees
        sun (float): Sun longitude in degrees
    
    Returns:
        tuple: (tithi: 1-30, karana: str name)
    """
    diff = (moon - sun) % 360.0  # Angular distance
    tithi = int(diff // 12) + 1   # Each 12° is one tithi
    
    if diff < 6.0:
        # Kimstughna occupies the first 6°
        karana = "Kimstughna"
    elif diff >= 342.0:
        # Last 3 fixed karanas: Shakuni, Chatushpada, Naga (each 6° wide)
        fixed = ["Shakuni", "Chatushpada", "Naga"]
        idx = int((diff - 342.0) // 6.0)
        if idx < 0:
            idx = 0
        elif idx > 2:
            idx = 2
        karana = fixed[idx]
    else:
        # Repeating 7 karanas cycle
        seq = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
        slot = int(diff // 6.0) - 1
        karana = seq[slot % 7]
    
    return tithi, karana


def bhadra_state(karana, moon):
    """
    Determine Bhadra state (inauspicious period during Vishti karana).
    Bhadra tail: Aries-Gemini (0-90°)
    Bhadra severe: Rest of zodiac (90-360°)
    
    Args:
        karana (str): Karana name
        moon (float): Moon longitude in degrees
    
    Returns:
        str: "none", "tail", or "severe"
    """
    if karana != "Vishti":
        return "none"
    if moon < 90:  # Aries–Gemini
        return "tail"
    return "severe"


# =================================================
# PANCHAK DETECTION
# =================================================

def is_panchak(moon):
    """
    Check if moon is in Panchak (inauspicious 5-day period).
    Panchak: Last 20° of Dhanishtha nakshatra through Revati.
    Moon longitude 300-360° (2nd half Dhanishtha → Revati)
    
    Args:
        moon (float): Moon longitude in degrees
    
    Returns:
        bool: True if in Panchak
    """
    return 300 <= moon < 360


# =================================================
# TARA BALA (JANMA NAKSHATRA BALANCE)
# =================================================

def tara_bala(janma_nak, moon_nak):
    """
    Calculate Tara Bala (strength based on birth nakshatra vs current nakshatra).
    Tara values 1, 3, 5, 7 are inauspicious (REJECT).
    
    Args:
        janma_nak (str): Birth nakshatra name
        moon_nak (str): Current moon nakshatra name
    
    Returns:
        tuple: (tara: 1-9, bala_score: 0-35)
    """
    j = NAKSHATRAS.index(janma_nak)
    m = NAKSHATRAS.index(moon_nak)
    dist = (m - j) % 27 + 1
    tara = ((dist - 1) % 9) + 1
    
    score_map = {
        1: 0, 3: 0, 5: 0, 7: 0,      # OVERRIDE REJECT
        2: 28, 4: 26, 6: 24, 8: 22, 9: 35
    }
    return tara, score_map[tara]


# =================================================
# CHANDRA RASHI BALA (JANMA RASHI BALANCE)
# =================================================

def chandra_rashi_bala(janma_rashi, moon_rashi):
    """
    Calculate Chandra Rashi Bala (strength based on birth sign vs current sign).
    Distances 6, 8, 12 are inauspicious (REJECT).
    
    Args:
        janma_rashi (str): Birth sign name
        moon_rashi (str): Current moon sign name
    
    Returns:
        dict: {
            "distance": 1-12,
            "score": 0-26,
            "override": bool (True = REJECT)
        }
    """
    j = RASHIS.index(janma_rashi)
    m = RASHIS.index(moon_rashi)
    dist = (m - j) % 12 + 1
    
    if dist in {6, 8, 12}:  # OVERRIDE REJECT
        return {"distance": dist, "score": 0, "override": True}
    
    if dist in {3, 5, 9, 11}:
        return {"distance": dist, "score": 26, "override": False}
    
    return {"distance": dist, "score": 15, "override": False}


# =================================================
# NAKSHATRA–TITHI YATRA YOGA (FALLBACK SCORING)
# =================================================

def nakshatra_tithi_yoga(nak, tithi):
    """
    Calculate fallback score when personal nakshatra/rashi data unavailable.
    Combines good/neutral nakshatra and tithi scores.
    
    Args:
        nak (str): Nakshatra name
        tithi (int): Tithi number (1-30)
    
    Returns:
        int: Combined score (0-25)
    """
    ns = 15 if nak in GOOD_NAK_YATRA else 8 if nak in NEUTRAL_NAK_YATRA else 0
    ts = 10 if tithi in GOOD_TITHI else 5 if tithi in NEUTRAL_TITHI else 0
    return ns + ts


# =================================================
# BIRTH NAKSHATRA CALCULATION
# =================================================

def janma_nakshatra_from_birth(dob, tob, lat, lon):
    """
    Calculate birth nakshatra from date of birth, time, and location.
    
    Args:
        dob (str): Date of birth in YYYY-MM-DD format
        tob (str): Time of birth in HH:MM format
        lat (float): Birth latitude
        lon (float): Birth longitude
    
    Returns:
        str: Janma nakshatra name
    """
    dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    dt_utc = to_utc(dt, lat, lon)
    jd = julian_day(dt_utc)
    moon = swe.calc_ut(jd, swe.MOON)[0][0] % 360
    return nakshatra_from_longitude(moon)


# =================================================
# MAIN PREDICTION ENGINE
# =================================================

def predict_travel(
    travel_dt, lat, lon, direction,
    dob=None, tob=None, pob_lat=None, pob_lon=None,
    janma_rashi=None,
    disha_remedy=False
):
    """
    Main travel prediction algorithm based on Vedic astrology.
    Analyzes multiple astrological factors to determine travel auspiciousness.
    
    Args:
        travel_dt (datetime): Proposed travel datetime
        lat (float): Travel starting latitude
        lon (float): Travel starting longitude
        direction (str): Travel direction (N, NE, E, SE, S, SW, W, NW)
        dob (str, optional): Birth date in YYYY-MM-DD format
        tob (str, optional): Birth time in HH:MM format
        pob_lat (float, optional): Birth place latitude
        pob_lon (float, optional): Birth place longitude
        janma_rashi (str, optional): Birth sign if nakshatra unknown
        disha_remedy (bool): Whether Disha Shool remedy applied
    
    Returns:
        dict: {
            "Score": 0-100,
            "Verdict": "AUSPICIOUS" | "NEUTRAL – Only if necessary" | "BAD – Avoid Travel",
            "Details": {
                "Moon Nakshatra": str,
                "Moon Rashi": str,
                "Janma Nakshatra": str or None,
                "Tithi": int,
                "Karana": str,
                "Bhadra": str,
                "Panchak": bool
            }
        }
    """
    # Convert travel time to UTC
    dt_utc = to_utc(travel_dt, lat, lon)
    moon, sun = moon_sun_longitudes(dt_utc)
    
    # Calculate basic astrological parameters
    nak = nakshatra_from_longitude(moon)
    rashi = rashi_from_longitude(moon)
    weekday = travel_dt.strftime("%A")
    tithi, karana = tithi_karana(moon, sun)
    bhadra = bhadra_state(karana, moon)
    panchak = is_panchak(moon)
    
    # Debug logging
    print("*" * 20)
    print(f"dt_utc : {dt_utc}")
    print(f"moon : {moon}")
    print(f"sun : {sun}")
    print(f"nak : {nak}")
    print(f"rashi : {rashi}")
    print(f"weekday : {weekday}")
    print(f"tithi : {tithi}")
    print(f"karana : {karana}")
    print(f"bhadra : {bhadra}")
    print(f"panchak : {panchak}")
    print("*" * 20)
    
    # Initial verdict for critical situations
    verdict = None
    bhadra_verdict = None
    panchak_verdict = None

    # Override 1: SEVERE BHADRA
    if bhadra == "severe":
        bhadra_verdict = "REJECT – Severe Bhadra"
    
    # Override 2: SEVERE PANCHAK
    if panchak and PANCHAK_TYPE[weekday] in {"Mrityu", "Shoka"}:
        panchak_verdict = "REJECT – Severe Panchak"
    
    # Determine Janma Nakshatra if birth data provided
    janma_nak = None
    if dob and tob and pob_lat is not None and pob_lon is not None:
        janma_nak = janma_nakshatra_from_birth(dob, tob, pob_lat, pob_lon)
    
    # Calculate personal balance score
    bala_score = 0
    
    if janma_nak:
        tara, bala_score = tara_bala(janma_nak, nak)
        if tara in {1, 3, 5, 7}:
            verdict = "REJECT – Bad Tara Bala"
    elif janma_rashi:
        rb = chandra_rashi_bala(janma_rashi, rashi)
        if rb["override"]:
            verdict = "REJECT – Bad Chandra Rashi Bala"
        bala_score = rb["score"]
    else:
        # Fallback: use nakshatra-tithi yoga
        bala_score = nakshatra_tithi_yoga(nak, tithi)
    print(f"bala_score : {bala_score}")
    # Final scoring (only if no critical rejects)
    if verdict is None:
        score = 0
        score += 30 if bhadra == "none" else 12
        score += 20 if not panchak else 5
        score += bala_score
        score += 15 if DISHA_SHOOL[weekday] != direction else (10 if disha_remedy else 4)
        
        verdict = (
            "AUSPICIOUS" if score >= 75 else
            "NEUTRAL – Only if necessary" if score >= 55 else
            "BAD – Avoid Travel"
        )
    else:
        score = 0
    
    return {
        "Score": score,
        "Verdict": verdict,
        "Details": {
            "Moon Nakshatra": nak,
            "Moon Rashi": rashi,
            "Janma Nakshatra": janma_nak,
            "Tithi": tithi,
            "Karana": karana,
            "Bhadra": bhadra,
            "Panchak": panchak,
            "nak": nak,
            "rashi": rashi,
            "weekday": weekday,
            "bhadra_verdict": bhadra_verdict,
            "panchak_verdict": panchak_verdict,
            "bala_score": bala_score,
            "direction": direction
        }
    }
