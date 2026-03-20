"""
Travel Prediction API using Swiss Ephemeris (pyswisseph)
Calculates Tara Bala, Bhadra, Panchak, Tithi, Karana, and Disha
"""

import swisseph as swe
from datetime import datetime, timezone
import math


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Tara Bala: position of travel nakshatra counted from Janma nakshatra
# Tara numbers and their quality
TARA_NAMES = {
    1: "Janma",        # Inauspicious
    2: "Sampat",       # Auspicious
    3: "Vipat",        # Inauspicious
    4: "Kshema",       # Auspicious
    5: "Pratyak",      # Inauspicious
    6: "Sadhaka",      # Auspicious
    7: "Vadha",        # Inauspicious
    8: "Mitra",        # Auspicious
    9: "Parama Mitra", # Auspicious
}

TARA_GOOD = {2, 4, 6, 8, 9}
TARA_BAD  = {1, 3, 5, 7}

# Panchak nakshatras: Dhanishtha (22) to Revati (26) → index 22–26 (0-based)
PANCHAK_NAKSHATRAS = {"Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"}

# Bhadra (Vishti Karana) — severely inauspicious for travel
VISHTI_KARANA = "Vishti"

# Karana names (11 karanas, each half-tithi)
KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija",
    "Vanija", "Vishti",  # 7 movable
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"  # 4 fixed
]

# Direction auspiciousness by weekday (traditional Disha Shool)
# Inauspicious direction for each weekday
DISHA_SHOOL = {
    "Sunday":    "West",
    "Monday":    "East",
    "Tuesday":   "North",
    "Wednesday": "North",
    "Thursday":  "South",
    "Friday":    "West",
    "Saturday":  "East",
}

# Nakshatra → ruling direction (for Panchak direction check)
NAKSHATRA_DIRECTION = {
    "Dhanishtha": "West",
    "Shatabhisha": "West",
    "Purva Bhadrapada": "West",
    "Uttara Bhadrapada": "North",
    "Revati": "North",
}

# Score weights
WEIGHT_TARA    = 40
WEIGHT_BHADRA  = 25
WEIGHT_PANCHAK = 15
WEIGHT_TITHI   = 10
WEIGHT_DISHA   = 10

# Inauspicious tithis for travel
BAD_TITHIS = {4, 8, 9, 12, 14, 15, 30}


# ─────────────────────────────────────────────
# REMEDIES LIBRARY
# ─────────────────────────────────────────────

# Each remedy entry:
#   cause        – internal key matching reject reason
#   title        – short display name
#   mantra       – mantra to chant (with count)
#   ritual       – physical ritual / puja steps
#   offering     – item to offer / donate
#   deity        – presiding deity to worship
#   timing       – best time to perform remedy
#   effect       – what the remedy neutralises
#   severity     – "mild" | "moderate" | "strong"  (strength of remedy needed)

REMEDIES = {

    # ── Tara Bala remedies (by Tara number) ──────────────────────────────
    "tara_janma": {
        "cause":    "Tara 1 – Janma",
        "title":    "Janma Tara Shanti",
        "mantra":   "Om Chandraya Namah (108 times before departure)",
        "ritual":   (
            "Offer white flowers and milk to a Shiva linga. "
            "Light a white sesame oil lamp facing East. "
            "Perform Chandra Namaskara 11 times."
        ),
        "offering": "White rice, white cloth, silver coin donated to a Brahmin",
        "deity":    "Lord Shiva / Chandra Dev",
        "timing":   "Monday morning before sunrise or during Brahma Muhurta",
        "effect":   "Neutralises Janma Tara danger for the journey",
        "severity": "strong",
    },
    "tara_vipat": {
        "cause":    "Tara 3 – Vipat",
        "title":    "Vipat Tara Shanti",
        "mantra":   "Om Namo Bhagavate Vasudevaya (108 times)",
        "ritual":   (
            "Worship Lord Vishnu with tulsi leaves and yellow flowers. "
            "Recite Vishnu Sahasranama or at minimum Vishnu Ashtottara. "
            "Light a ghee lamp with 5 wicks."
        ),
        "offering": "Yellow sweets, yellow cloth, gold/copper coin to temple",
        "deity":    "Lord Vishnu / Narayana",
        "timing":   "Thursday morning or evening of travel day",
        "effect":   "Removes obstacles and dangers indicated by Vipat Tara",
        "severity": "strong",
    },
    "tara_pratyak": {
        "cause":    "Tara 5 – Pratyak",
        "title":    "Pratyak Tara Shanti",
        "mantra":   "Om Gam Ganapataye Namah (108 times)",
        "ritual":   (
            "Worship Lord Ganesha with red flowers and modak. "
            "Apply vermillion tilak on forehead. "
            "Recite Ganesh Atharvashirsha once."
        ),
        "offering": "Coconut, jaggery, red cloth at Ganesha temple",
        "deity":    "Lord Ganesha",
        "timing":   "Before stepping out of home on the day of travel",
        "effect":   "Eliminates reversal energy of Pratyak Tara",
        "severity": "moderate",
    },
    "tara_vadha": {
        "cause":    "Tara 7 – Vadha",
        "title":    "Vadha Tara Shanti",
        "mantra":   "Om Hanumate Namah (108 times) + Hanuman Chalisa recitation",
        "ritual":   (
            "Visit a Hanuman temple before travel. "
            "Offer sindoor mixed in oil to Hanuman idol. "
            "Light 7 mustard oil lamps. "
            "Tie a red thread (raksha sutra) on right wrist."
        ),
        "offering": "Besan ladoo, red flowers, red cloth at Hanuman temple",
        "deity":    "Lord Hanuman",
        "timing":   "Tuesday or Saturday morning before departure",
        "effect":   "Provides strong protection against Vadha Tara harm",
        "severity": "strong",
    },

    # ── Bhadra / Vishti Karana ────────────────────────────────────────────
    "bhadra_severe": {
        "cause":    "Severe Bhadra (Vishti Karana)",
        "title":    "Severe Bhadra Shanti",
        "mantra":   "Om Namo Bhagavate Vasudevaya (108 times) + Mahamrityunjaya Mantra (11 times)",
        "ritual":   (
            "Strictly avoid travel during Bhadra period if possible — wait for it to pass. "
            "If unavoidable: perform Mahamrityunjaya Homa or have it performed by a priest. "
            "Take blessing of elders / parents before leaving. "
            "Carry a Rudraksha mala (5-mukhi) throughout the journey."
        ),
        "offering": "Black sesame seeds in flowing water (river/tap), black cloth donation",
        "deity":    "Lord Shiva (Mahamrityunjaya form)",
        "timing":   "Start travel only after Bhadra period ends (check Panchang for end time)",
        "effect":   "Mitigates severe Bhadra — ideally delay travel until Bhadra ends",
        "severity": "strong",
    },
    "bhadra_moderate": {
        "cause":    "Moderate Bhadra (Vishti Karana)",
        "title":    "Bhadra Shanti",
        "mantra":   "Om Namo Bhagavate Vasudevaya (21 times)",
        "ritual":   (
            "Worship Lord Vishnu or Shiva briefly before departing. "
            "Eat a spoonful of curd and sugar (dahi-shakkar) before leaving home. "
            "Carry a small Hanuman yantra or Rudraksha bead."
        ),
        "offering": "White flowers, milk, rice at home temple or nearest temple",
        "deity":    "Lord Vishnu",
        "timing":   "Morning of travel before 9 AM",
        "effect":   "Softens moderate Bhadra impact on the journey",
        "severity": "moderate",
    },

    # ── Panchak ───────────────────────────────────────────────────────────
    "panchak": {
        "cause":    "Panchak",
        "title":    "Panchak Shanti",
        "mantra":   "Om Panchakaaya Namah (108 times)",
        "ritual":   (
            "Light a 5-wicked ghee lamp (pancha-deepa) and pray to Pancha Devatas. "
            "Recite Navgraha stotra focusing on Chandra and Rahu. "
            "Feed 5 Brahmins or donate to 5 people before travel. "
            "Perform Navagraha puja if possible."
        ),
        "offering": "5 types of grain (pancha dhanya) donated, blue/black cloth",
        "deity":    "Pancha Devatas / Navagraha",
        "timing":   "One day before travel during evening puja",
        "effect":   "Reduces five-fold inauspiciousness of Panchak nakshatra",
        "severity": "moderate",
    },

    # ── Inauspicious Tithi ────────────────────────────────────────────────
    "bad_tithi": {
        "cause":    "Inauspicious Tithi",
        "title":    "Tithi Shanti",
        "mantra":   "Om Suryaya Namah (12 times) + Om Somaya Namah (12 times)",
        "ritual":   (
            "Perform Surya Arghya (water offering to Sun) in the morning. "
            "Light an oil lamp at a Devi temple. "
            "Recite Durga Kavach or Devi Stuti once."
        ),
        "offering": "Red flowers, coconut, and fruits at Devi temple",
        "deity":    "Goddess Durga / Devi",
        "timing":   "Morning of travel day during Abhijit Muhurta (around noon) if possible",
        "effect":   "Counteracts negative energy of inauspicious tithi",
        "severity": "mild",
    },

    # ── Disha Shool ───────────────────────────────────────────────────────
    "disha_east": {
        "cause":    "Disha Shool – East",
        "title":    "Disha Shool Remedy (East)",
        "mantra":   "Om Indraya Namah (21 times)",
        "ritual":   (
            "Consume a piece of jaggery (gur) before leaving. "
            "Alternatively, eat curd-rice before departure. "
            "Take 3 steps back inside the home before finally stepping out East."
        ),
        "offering": "Jaggery offered at home altar",
        "deity":    "Indra Dev (East direction lord)",
        "timing":   "Immediately before departure",
        "effect":   "Nullifies Monday/Tuesday Disha Shool for East direction",
        "severity": "mild",
    },
    "disha_west": {
        "cause":    "Disha Shool – West",
        "title":    "Disha Shool Remedy (West)",
        "mantra":   "Om Varunaya Namah (21 times)",
        "ritual":   (
            "Eat a piece of white sweet (mishri or barfi) before leaving. "
            "Keep a small silver piece or coin in your pocket during travel. "
            "Offer water to a Peepal tree before departure if possible."
        ),
        "offering": "White sweets, white flowers at home altar or Shiva temple",
        "deity":    "Varuna Dev (West direction lord)",
        "timing":   "Immediately before departure",
        "effect":   "Nullifies Sunday/Friday Disha Shool for West direction",
        "severity": "mild",
    },
    "disha_north": {
        "cause":    "Disha Shool – North",
        "title":    "Disha Shool Remedy (North)",
        "mantra":   "Om Kuberaya Namah (21 times)",
        "ritual":   (
            "Eat mustard seeds or mustard oil-based food before leaving. "
            "Offer a coconut at a Ganesha or Kubera temple. "
            "Wear yellow or carry yellow turmeric before departure."
        ),
        "offering": "Yellow cloth, turmeric, coconut at Ganesha temple",
        "deity":    "Kubera Dev (North direction lord)",
        "timing":   "Morning of travel day",
        "effect":   "Nullifies Tuesday/Wednesday Disha Shool for North direction",
        "severity": "mild",
    },
    "disha_south": {
        "cause":    "Disha Shool – South",
        "title":    "Disha Shool Remedy (South)",
        "mantra":   "Om Yamaya Namah (21 times)",
        "ritual":   (
            "Offer black sesame seeds (til) in running water before travel. "
            "Light a mustard oil lamp at a Hanuman or Shani temple. "
            "Carry an iron nail or small iron piece (Shani remedy) in your bag."
        ),
        "offering": "Black sesame, mustard oil lamp, black cloth at Shani/Hanuman temple",
        "deity":    "Yama Dev / Lord Hanuman (South direction)",
        "timing":   "Before 8 AM on the travel day",
        "effect":   "Nullifies Thursday Disha Shool for South direction",
        "severity": "moderate",
    },
}

# Tara number → remedy key mapping
TARA_REMEDY_MAP = {
    1: "tara_janma",
    3: "tara_vipat",
    5: "tara_pratyak",
    7: "tara_vadha",
}

# Direction → Disha Shool remedy key
DISHA_REMEDY_MAP = {
    "east":  "disha_east",
    "west":  "disha_west",
    "north": "disha_north",
    "south": "disha_south",
}


def _build_remedies(
    tara_num: int,
    tara_good: bool,
    is_bhadra: bool,
    bhadra_severity: str,
    is_panchak: bool,
    tithi_score_val: int,
    disha_score_val: int,
    direction: str,
) -> list:
    """
    Build a list of applicable remedy dicts based on what failed.
    Each remedy includes:
      - cause, title, mantra, ritual, offering, deity, timing, effect, severity
      - can_travel_with_remedy (bool) — True unless Severe Bhadra
    """
    remedies = []

    # Tara Bala remedy
    if not tara_good and tara_num in TARA_REMEDY_MAP:
        r = dict(REMEDIES[TARA_REMEDY_MAP[tara_num]])
        r["can_travel_with_remedy"] = True
        remedies.append(r)

    # Bhadra remedy
    if is_bhadra:
        key = "bhadra_severe" if bhadra_severity == "severe" else "bhadra_moderate"
        r = dict(REMEDIES[key])
        # Severe Bhadra: strongly advise NOT to travel even with remedy
        r["can_travel_with_remedy"] = bhadra_severity != "severe"
        remedies.append(r)

    # Panchak remedy
    if is_panchak:
        r = dict(REMEDIES["panchak"])
        r["can_travel_with_remedy"] = True
        remedies.append(r)

    # Tithi remedy
    if tithi_score_val == 0:
        r = dict(REMEDIES["bad_tithi"])
        r["can_travel_with_remedy"] = True
        remedies.append(r)

    # Disha Shool remedy
    if disha_score_val == 0:
        dir_key = direction.strip().lower()
        if dir_key in DISHA_REMEDY_MAP:
            r = dict(REMEDIES[DISHA_REMEDY_MAP[dir_key]])
            r["can_travel_with_remedy"] = True
            remedies.append(r)

    return remedies


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _to_jd(dt: datetime) -> float:
    """Convert a timezone-aware (or naive UTC) datetime to Julian Day."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ut = dt.utctimetuple()
    hour_frac = ut.tm_hour + ut.tm_min / 60.0 + ut.tm_sec / 3600.0
    return swe.julday(ut.tm_year, ut.tm_mon, ut.tm_mday, hour_frac)


def _moon_longitude(jd: float) -> float:
    """Return Moon's ecliptic longitude (sidereal, Lahiri ayanamsa)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    result, _ = swe.calc_ut(jd, swe.MOON, flags)
    return result[0]  # degrees 0–360


def _sun_longitude(jd: float) -> float:
    """Return Sun's ecliptic longitude (sidereal, Lahiri)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    result, _ = swe.calc_ut(jd, swe.SUN, flags)
    return result[0]


def _nakshatra_from_lon(lon: float):
    """Return (nakshatra_name, pada) from sidereal longitude."""
    nak_idx = int(lon / (360 / 27))
    pada    = int((lon % (360 / 27)) / (360 / 108)) + 1
    return NAKSHATRAS[nak_idx % 27], pada


def _rashi_from_lon(lon: float) -> str:
    return RASHIS[int(lon / 30) % 12]


def _tithi(moon_lon: float, sun_lon: float) -> int:
    """Tithi 1–30."""
    diff = (moon_lon - sun_lon) % 360
    return int(diff / 12) + 1


def _karana(moon_lon: float, sun_lon: float) -> str:
    """Return Karana name."""
    diff = (moon_lon - sun_lon) % 360
    half_tithi_index = int(diff / 6)  # 0-based, 0–59
    # First half of tithi 1 is Kimstughna (fixed)
    if half_tithi_index == 0:
        return "Kimstughna"
    # Last half of tithi 30 is Shakuni
    if half_tithi_index == 59:
        return "Shakuni"
    movable_index = (half_tithi_index - 1) % 7
    return KARANA_NAMES[movable_index]


def _tara_bala(janma_nak: str, travel_nak: str):
    """
    Calculate Tara Bala.
    Returns (tara_number, tara_name, is_good, bala_score 0 or WEIGHT_TARA)
    """
    j_idx = NAKSHATRAS.index(janma_nak)
    t_idx = NAKSHATRAS.index(travel_nak)
    count = ((t_idx - j_idx) % 27) + 1  # 1–27
    tara_num = ((count - 1) % 9) + 1    # 1–9
    tara_name = TARA_NAMES[tara_num]
    is_good = tara_num in TARA_GOOD
    score = WEIGHT_TARA if is_good else 0
    return tara_num, tara_name, is_good, score


def _bhadra_check(karana: str, tithi: int):
    """
    Bhadra (Vishti Karana) check.
    Returns (is_bhadra: bool, severity: str|None, score: int)
    """
    if karana != VISHTI_KARANA:
        return False, None, WEIGHT_BHADRA

    # Severity based on tithi half
    severe_tithis = {4, 8, 11, 19, 26}  # traditional severe Bhadra tithis
    if tithi in severe_tithis:
        severity = "severe"
    else:
        severity = "moderate"
    return True, severity, 0


def _panchak_check(travel_nak: str, direction: str):
    """
    Returns (is_panchak: bool, verdict: str|None, score: int)
    """
    if travel_nak not in PANCHAK_NAKSHATRAS:
        return False, None, WEIGHT_PANCHAK

    # Extra penalty if direction matches panchak nakshatra direction
    nak_dir = NAKSHATRA_DIRECTION.get(travel_nak, "")
    if nak_dir.lower() == direction.strip().lower():
        verdict = "REJECT – Panchak (direction conflict)"
    else:
        verdict = "CAUTION – Panchak active"
    return True, verdict, 0


def _tithi_score(tithi: int) -> int:
    if tithi in BAD_TITHIS:
        return 0
    return WEIGHT_TITHI


def _disha_score(weekday: str, direction: str) -> int:
    """Disha Shool check. Returns 0 if direction matches inauspicious direction."""
    bad_dir = DISHA_SHOOL.get(weekday, "")
    if bad_dir.lower() == direction.strip().lower():
        return 0
    return WEIGHT_DISHA


def _parse_date(value):
    """
    Accept dob as:
      - datetime / date object  → returned as-is
      - "YYYY-MM-DD"            → parsed to date
      - "DD-MM-YYYY"            → parsed to date
      - "DD/MM/YYYY"            → parsed to date
      - "YYYY/MM/DD"            → parsed to date
    """
    if value is None:
        return None
    if hasattr(value, "year"):          # already a date/datetime
        return value
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse dob '{value}'. "
        "Accepted formats: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, YYYY/MM/DD"
    )


def _parse_time(value):
    """
    Accept tob as:
      - datetime / time object  → returned as-is
      - "HH:MM"                 → parsed to datetime (date part ignored)
      - "HH:MM:SS"              → parsed to datetime
      - "HH:MM AM/PM"           → parsed to datetime
    """
    if value is None:
        return None
    if hasattr(value, "hour"):          # already a time/datetime
        return value
    value = str(value).strip()
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse tob '{value}'. "
        "Accepted formats: HH:MM, HH:MM:SS, HH:MM AM/PM"
    )


def _parse_travel_dt(value):
    """
    Accept travel_dt as:
      - datetime object  → returned as-is
      - "YYYY-MM-DD HH:MM:SS"
      - "YYYY-MM-DD HH:MM"
      - "YYYY-MM-DDTHH:MM:SS"  (ISO 8601)
      - "YYYY-MM-DDTHH:MM"
    """
    if value is None:
        raise ValueError("travel_dt is required.")
    if hasattr(value, "year") and hasattr(value, "hour"):
        return value
    value = str(value).strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse travel_dt '{value}'. "
        "Accepted formats: YYYY-MM-DD HH:MM:SS, YYYY-MM-DDTHH:MM:SS, DD-MM-YYYY HH:MM"
    )


def _janma_nakshatra_from_birth(dob, tob, pob_lat: float, pob_lon: float) -> tuple:
    """
    Compute Janma Nakshatra (and Rashi) from birth details.
    Accepts dob/tob as datetime objects OR strings.
    Returns (janma_nak, janma_rashi)
    """
    dob = _parse_date(dob)
    tob = _parse_time(tob)

    tz = tob.tzinfo if hasattr(tob, "tzinfo") else None
    birth_dt = datetime(
        dob.year, dob.month, dob.day,
        tob.hour, tob.minute, tob.second,
        tzinfo=tz
    )
    jd = _to_jd(birth_dt)
    moon_lon = _moon_longitude(jd)
    nak, _ = _nakshatra_from_lon(moon_lon)
    rashi = _rashi_from_lon(moon_lon)
    return nak, rashi


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────

def predict_travel(
    travel_dt,
    lat,
    lon,
    direction,
    dob=None,
    tob=None,
    pob_lat=None,
    pob_lon=None,
    janma_rashi=None,
    disha_remedy=False
):
    """
    Predict travel auspiciousness.

    Parameters
    ----------
    travel_dt   : datetime  – date & time of travel (timezone-aware or UTC)
    lat         : float     – latitude of departure location
    lon         : float     – longitude of departure location
    direction   : str       – travel direction e.g. "North", "South", "East", "West"
    dob         : date/datetime (optional) – date of birth
    tob         : time/datetime (optional) – time of birth
    pob_lat     : float (optional) – birth place latitude
    pob_lon     : float (optional) – birth place longitude
    janma_rashi : str (optional)   – override Janma Rashi directly
    disha_remedy: bool             – if True, suppress Disha Shool rejection

    Returns
    -------
    dict with status, status_code, response
    """

    # ── 0. Parse / normalise inputs ─────────────
    travel_dt = _parse_travel_dt(travel_dt)
    dob       = _parse_date(dob)
    tob       = _parse_time(tob)

    # ── 1. Travel day panchang ──────────────────
    jd = _to_jd(travel_dt)
    moon_lon = _moon_longitude(jd)
    sun_lon  = _sun_longitude(jd)

    moon_nak, moon_pada = _nakshatra_from_lon(moon_lon)
    moon_rashi          = _rashi_from_lon(moon_lon)

    tithi_num = _tithi(moon_lon, sun_lon)
    karana    = _karana(moon_lon, sun_lon)

    # Python weekday(): Monday=0 … Sunday=6
    weekday = WEEKDAYS[travel_dt.weekday()]

    # ── 2. Janma Nakshatra resolution ───────────
    birth_data_available = all(v is not None for v in [dob, tob, pob_lat, pob_lon])

    if birth_data_available:
        # Derive from birth chart
        janma_nak, janma_rashi_calc = _janma_nakshatra_from_birth(dob, tob, pob_lat, pob_lon)
        if janma_rashi is None:
            janma_rashi = janma_rashi_calc
        using_chandra_fallback = False
    else:
        # Fallback: use Chandra (Moon) nakshatra at travel time as Janma
        janma_nak   = moon_nak
        janma_rashi = moon_rashi
        using_chandra_fallback = True

    # ── 3. Scoring ──────────────────────────────
    tara_num, tara_name, tara_good, tara_score = _tara_bala(janma_nak, moon_nak)

    is_bhadra, bhadra_severity, bhadra_score = _bhadra_check(karana, tithi_num)

    is_panchak, panchak_verdict, panchak_score = _panchak_check(moon_nak, direction)

    tithi_score_val = _tithi_score(tithi_num)

    disha_score_val = 0 if disha_remedy else _disha_score(weekday, direction)

    total_score = tara_score + bhadra_score + panchak_score + tithi_score_val + disha_score_val

    # ── 4. Verdicts ─────────────────────────────
    reject_reasons = []
    if not tara_good:
        reject_reasons.append(f"Bad Tara Bala ({tara_name})")
    if is_bhadra:
        reject_reasons.append(f"{'Severe' if bhadra_severity == 'severe' else 'Moderate'} Bhadra")
    if is_panchak:
        reject_reasons.append("Panchak")
    if tithi_score_val == 0:
        reject_reasons.append(f"Inauspicious Tithi ({tithi_num})")
    if disha_score_val == 0 and not disha_remedy:
        reject_reasons.append(f"Disha Shool ({direction})")

    if reject_reasons:
        verdict = "REJECT – " + ", ".join(reject_reasons)
    elif total_score >= 80:
        verdict = "ACCEPT – Highly Auspicious"
    elif total_score >= 60:
        verdict = "ACCEPT – Moderately Auspicious"
    else:
        verdict = "CAUTION – Marginally Auspicious"

    bhadra_verdict = (
        f"REJECT – {'Severe' if bhadra_severity == 'severe' else 'Moderate'} Bhadra"
        if is_bhadra else None
    )

    # ── 5. Build remedies ───────────────────────
    remedies = []
    if reject_reasons:
        remedies = _build_remedies(
            tara_num        = tara_num,
            tara_good       = tara_good,
            is_bhadra       = is_bhadra,
            bhadra_severity = bhadra_severity,
            is_panchak      = is_panchak,
            tithi_score_val = tithi_score_val,
            disha_score_val = disha_score_val,
            direction       = direction,
        )

    can_travel_after_remedy = all(r.get("can_travel_with_remedy", True) for r in remedies)

    remedy_summary = None
    if remedies:
        if can_travel_after_remedy:
            remedy_summary = (
                "Travel is permitted after performing the listed remedies. "
                "Complete all rituals before departure for full protection."
            )
        else:
            remedy_summary = (
                "Severe Bhadra is active. It is strongly advised NOT to travel during this period. "
                "If absolutely unavoidable, perform all listed remedies and travel only after "
                "Bhadra ends (check today's Panchang for exact end time)."
            )

    # ── 6. Build response ───────────────────────
    details = {
        "Moon Nakshatra":  moon_nak,
        "Moon Rashi":      moon_rashi,
        "Janma Nakshatra": janma_nak,
        "Janma Rashi":     janma_rashi,
        "Tithi":           tithi_num,
        "Karana":          karana,
        "Bhadra":          bhadra_severity if is_bhadra else False,
        "Panchak":         is_panchak,
        "nak":             moon_nak,
        "rashi":           moon_rashi,
        "weekday":         weekday,
        "bhadra_verdict":  bhadra_verdict,
        "panchak_verdict": panchak_verdict,
        "bala_score":      tara_score,
        "direction":       direction.capitalize(),
        "tara_number":     tara_num,
        "tara_name":       tara_name,
        "used_chandra_fallback": using_chandra_fallback,
    }

    status_code = "200" if not reject_reasons else "202"

    response_body = {
        "Score":   total_score,
        "Verdict": verdict,
        "Details": details,
        "Remedies": {
            "summary":                 remedy_summary,
            "can_travel_after_remedy": can_travel_after_remedy,
            "count":                   len(remedies),
            "items":                   remedies,
        } if remedies else None,
    }

    return {
        "status":      "success",
        "status_code": status_code,
        "response":    response_body,
    }


# ─────────────────────────────────────────────
# EXAMPLE USAGE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # Example 1 – with birth details
    result = predict_travel(
        travel_dt = datetime(2025, 7, 19, 8, 0, 0, tzinfo=timezone.utc),
        lat       = 19.0760,
        lon       = 72.8777,
        direction = "South",
        dob       = datetime(1990, 5, 15),
        tob       = datetime(1990, 5, 15, 10, 30, 0, tzinfo=timezone.utc),
        pob_lat   = 19.0760,
        pob_lon   = 72.8777,
    )
    print("── With Birth Details ──")
    print(json.dumps(result, indent=4))

    print()

    # Example 2 – without birth details (Chandra fallback)
    result2 = predict_travel(
        travel_dt = datetime(2025, 7, 19, 8, 0, 0, tzinfo=timezone.utc),
        lat       = 19.0760,
        lon       = 72.8777,
        direction = "South",
    )
    print("── Without Birth Details (Chandra Fallback) ──")
    print(json.dumps(result2, indent=4))