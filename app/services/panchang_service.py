import swisseph as swe
import datetime
import pytz
import geopandas as gpd
from astral import LocationInfo
from astral.sun import sun
from pathlib import Path

# -------- CONFIG --------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SHP_PATH = BASE_DIR / "static" / "shp" / "india_places.shp"

TIMEZONE = "Asia/Kolkata"

IST = pytz.timezone(TIMEZONE)


# -------- PANCHANG LISTS --------

NAKSHATRA = [
"Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
"Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
"Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
"Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
"Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
"Uttara Bhadrapada","Revati"
]

TITHI = [
"Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
"Shashthi","Saptami","Ashtami","Navami","Dashami",
"Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima/Amavasya"
]

KARANA = [
"Bava","Balava","Kaulava","Taitila","Garaja",
"Vanija","Vishti","Shakuni","Chatushpada","Nagava"
]

YOGA = [
"Vishkumbha","Preeti","Ayushman","Saubhagya","Shobhana",
"Atiganda","Sukarma","Dhriti","Shoola","Ganda",
"Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
"Siddhi","Vyatipata","Variyana","Parigha","Shiva",
"Siddha","Sadhya","Shubha","Shukla","Brahma",
"Indra","Vaidhriti"
]


# -------- GET LAT LON FROM SHAPEFILE --------

def get_lat_lon(city):

    gdf = gpd.read_file(SHP_PATH)

    row = gdf[gdf["name"].str.lower() == city.lower()]

    if row.empty:
        raise Exception("City not found in shapefile")

    point = row.iloc[0].geometry

    lat = point.y
    lon = point.x

    return lat, lon


# -------- SUN TIMES --------

def get_sun_times(city, lat, lon):

    loc = LocationInfo(city, "India", TIMEZONE, lat, lon)

    s = sun(loc.observer, date=datetime.date.today(), tzinfo=IST)

    return s["sunrise"], s["sunset"]


# -------- PANCHANG CALCULATION --------

def calculate_panchang():

    now = datetime.datetime.now(IST)

    jd = swe.julday(
        now.year,
        now.month,
        now.day,
        now.hour + now.minute/60
    )

    sun_long = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_long = swe.calc_ut(jd, swe.MOON)[0][0]

    diff = (moon_long - sun_long) % 360

    tithi_index = int(diff / 12)
    tithi = TITHI[tithi_index % 15]

    nak_index = int(moon_long / (360/27))
    nakshatra = NAKSHATRA[nak_index]

    yoga_index = int(((sun_long + moon_long) % 360) / (360/27))
    yoga = YOGA[yoga_index]

    karana_index = int(diff / 6)
    karana = KARANA[karana_index % len(KARANA)]

    return tithi, nakshatra, yoga, karana


# -------- RAHU KAAL --------

def rahu_kaal(sunrise, sunset):

    day_duration = (sunset - sunrise) / 8
    weekday = datetime.datetime.today().weekday()

    rahu_slots = [1,6,4,5,3,2,7]

    start = sunrise + day_duration * rahu_slots[weekday]
    end = start + day_duration

    return start, end


# -------- YAMAGANDHA --------

def yamagandha(sunrise, sunset):

    day_duration = (sunset - sunrise) / 8
    weekday = datetime.datetime.today().weekday()

    slots = [4,3,2,1,0,6,5]

    start = sunrise + day_duration * slots[weekday]
    end = start + day_duration

    return start, end


# -------- GULIKA --------

def gulika(sunrise, sunset):

    day_duration = (sunset - sunrise) / 8
    weekday = datetime.datetime.today().weekday()

    slots = [6,5,4,3,2,1,0]

    start = sunrise + day_duration * slots[weekday]
    end = start + day_duration

    return start, end


# -------- ABHIJIT MUHURAT --------

def abhijit(sunrise, sunset):

    midday = sunrise + (sunset - sunrise)/2

    start = midday - datetime.timedelta(minutes=24)
    end = midday + datetime.timedelta(minutes=24)

    return start, end


# -------- MAIN PANCHANG --------

def get_panchang(city):

    lat, lon = get_lat_lon(city)

    sunrise, sunset = get_sun_times(city, lat, lon)

    tithi, nakshatra, yoga, karana = calculate_panchang()

    rahu_start, rahu_end = rahu_kaal(sunrise, sunset)
    yam_start, yam_end = yamagandha(sunrise, sunset)
    gul_start, gul_end = gulika(sunrise, sunset)

    abhi_start, abhi_end = abhijit(sunrise, sunset)

    response = {

        "city": city,
        "date": str(datetime.date.today()),

        "five_limb": {
            "tithi": tithi,
            "nakshatra": nakshatra,
            "yoga": yoga,
            "karana": karana
        },

        "important_time": {
            "sunrise": sunrise.strftime("%H:%M"),
            "sunset": sunset.strftime("%H:%M")
        },

        "inauspicious_time": {
            "rahu_kaal": f"{rahu_start.strftime('%H:%M')} - {rahu_end.strftime('%H:%M')}",
            "yamagandha": f"{yam_start.strftime('%H:%M')} - {yam_end.strftime('%H:%M')}",
            "gulika": f"{gul_start.strftime('%H:%M')} - {gul_end.strftime('%H:%M')}"
        },

        "auspicious_time": {
            "abhijit_muhurat": f"{abhi_start.strftime('%H:%M')} - {abhi_end.strftime('%H:%M')}"
        }

    }

    return response


# -------- RUN --------

if __name__ == "__main__":


    data = get_panchang("pune")

    print(data)