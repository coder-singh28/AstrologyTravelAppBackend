"""
Generic Astrology Remedies Engine
==================================
Covers:
  - Planet-wise remedies (all 9 Grahas)
  - Dosha remedies (Mangal, Kaal Sarp, Pitru, Shani Sade Sati, Guru Chandal)
  - Life area remedies (health, wealth, relationship, career, education, legal)
  - Transit-based remedies (current planetary positions)
  - Birth-chart-based weak planet detection (via swisseph)

Main entry point:
    get_remedies(...)
"""

import swisseph as swe
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

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

RASHI_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Debilitation signs — planet is weakest here
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Sagittarius", "Ketu": "Gemini"
}

# Exaltation signs — planet is strongest here
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Gemini", "Ketu": "Sagittarius"
}

# Enemy signs for each planet (rough classical mapping)
ENEMY_SIGNS = {
    "Sun":     ["Libra", "Aquarius"],
    "Moon":    ["Scorpio", "Capricorn"],
    "Mars":    ["Cancer", "Gemini"],
    "Mercury": ["Pisces", "Sagittarius"],
    "Jupiter": ["Capricorn", "Gemini"],
    "Venus":   ["Virgo", "Aries"],
    "Saturn":  ["Aries", "Cancer", "Leo"],
    "Rahu":    ["Sagittarius", "Pisces"],
    "Ketu":    ["Gemini", "Virgo"],
}

# SwissEph planet IDs
SWE_PLANETS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mars":    swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus":   swe.VENUS,
    "Saturn":  swe.SATURN,
}
# Rahu/Ketu via mean node
SWE_RAHU = swe.MEAN_NODE

WEEKDAY_PLANET = {
    "Sunday":    "Sun",
    "Monday":    "Moon",
    "Tuesday":   "Mars",
    "Wednesday": "Mercury",
    "Thursday":  "Jupiter",
    "Friday":    "Venus",
    "Saturday":  "Saturn",
}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ─────────────────────────────────────────────────────────────────────────────
# PLANET REMEDY LIBRARY
# Each planet has: mantra, gemstone, yantra, fasting_day, charity,
#                  puja, color, food, deity, metal, rudraksha
# ─────────────────────────────────────────────────────────────────────────────

PLANET_REMEDIES = {
    "Sun": {
        "planet":       "Sun (Surya)",
        "deity":        "Lord Surya / Lord Vishnu / Lord Ram",
        "mantra": {
            "beej":     "Om Hraam Hreem Hraum Sah Suryaya Namah",
            "vedic":    "Om Suryaya Namah",
            "gayatri":  "Om Bhaskaraya Vidmahe Mahadyutikaraya Dheemahi Tanno Adityah Prachodayat",
            "count":    108,
            "day":      "Sunday"
        },
        "gemstone": {
            "primary":  "Ruby (Manik)",
            "substitute": ["Red Garnet", "Red Spinel"],
            "weight":   "3–5 Ratti",
            "metal":    "Gold",
            "finger":   "Ring finger",
            "day":      "Sunday morning",
            "note":     "Wear only after consulting an astrologer"
        },
        "yantra":       "Surya Yantra — energise on Sunday during sunrise",
        "fasting": {
            "day":      "Sunday",
            "rules":    "Eat only once, avoid salt, eat wheat/jaggery based food"
        },
        "charity": [
            "Donate wheat, jaggery, red cloth, copper vessel on Sundays",
            "Feed jaggery-wheat bread to a cow",
            "Donate to a blind person or eye hospital"
        ],
        "puja": [
            "Perform Surya Arghya (water offering to Sun) daily at sunrise",
            "Recite Aditya Hridayam daily",
            "Light ghee lamp facing East every morning"
        ],
        "color":        ["Orange", "Red", "Gold", "Copper"],
        "avoid_color":  ["Black", "Dark Blue"],
        "food":         ["Wheat", "Jaggery", "Orange fruits", "Saffron"],
        "metal":        "Copper",
        "rudraksha":    "1 Mukhi (Ek Mukhi) Rudraksha",
        "life_areas":   ["career", "health", "father", "authority", "confidence"],
    },

    "Moon": {
        "planet":       "Moon (Chandra)",
        "deity":        "Lord Shiva / Goddess Parvati",
        "mantra": {
            "beej":     "Om Shraam Shreem Shraum Sah Chandraaya Namah",
            "vedic":    "Om Chandraya Namah",
            "gayatri":  "Om Ksheerputraya Vidmahe Amrittattvaya Dheemahi Tanno Chandrah Prachodayat",
            "count":    108,
            "day":      "Monday"
        },
        "gemstone": {
            "primary":  "Pearl (Moti)",
            "substitute": ["Moonstone", "White Coral"],
            "weight":   "4–6 Ratti",
            "metal":    "Silver",
            "finger":   "Little finger",
            "day":      "Monday morning",
            "note":     "Best during Shukla Paksha (waxing Moon)"
        },
        "yantra":       "Chandra Yantra — energise on Monday during moonrise",
        "fasting": {
            "day":      "Monday",
            "rules":    "Avoid non-veg and alcohol; eat milk, rice, white foods"
        },
        "charity": [
            "Donate white rice, white cloth, silver, milk on Mondays",
            "Feed kheer (rice pudding) to a Brahmin",
            "Donate to a women's shelter or old-age home"
        ],
        "puja": [
            "Offer milk/water to Shiva Linga on Mondays",
            "Recite Chandra Kavach or Chandra Ashtottara",
            "Keep silver bowl with water under moonlight on full moon night"
        ],
        "color":        ["White", "Silver", "Cream", "Pearl"],
        "avoid_color":  ["Red", "Dark Brown"],
        "food":         ["Rice", "Milk", "Curd", "White foods", "Coconut"],
        "metal":        "Silver",
        "rudraksha":    "2 Mukhi Rudraksha",
        "life_areas":   ["mind", "mother", "emotions", "health", "relationships"],
    },

    "Mars": {
        "planet":       "Mars (Mangal / Kuja)",
        "deity":        "Lord Hanuman / Lord Kartikeya / Lord Ganesha",
        "mantra": {
            "beej":     "Om Kraam Kreem Kraum Sah Bhaumaya Namah",
            "vedic":    "Om Mangalaya Namah",
            "gayatri":  "Om Veeradhwajaya Vidmahe Vighna Hasthaya Dheemahi Tanno Bhoumah Prachodayat",
            "count":    108,
            "day":      "Tuesday"
        },
        "gemstone": {
            "primary":  "Red Coral (Moonga)",
            "substitute": ["Carnelian", "Red Jasper"],
            "weight":   "6–9 Ratti",
            "metal":    "Gold or Copper",
            "finger":   "Ring finger",
            "day":      "Tuesday morning",
            "note":     "Especially useful for Manglik individuals"
        },
        "yantra":       "Mangal Yantra — energise on Tuesday at sunrise",
        "fasting": {
            "day":      "Tuesday",
            "rules":    "Eat only once; red-coloured foods, avoid non-veg"
        },
        "charity": [
            "Donate red lentils (masoor dal), red cloth, copper on Tuesdays",
            "Feed jaggery to monkeys",
            "Donate blood or to a military/police welfare fund"
        ],
        "puja": [
            "Visit Hanuman temple every Tuesday",
            "Recite Hanuman Chalisa 3x on Tuesdays",
            "Light mustard oil lamp at Hanuman temple"
        ],
        "color":        ["Red", "Coral", "Saffron"],
        "avoid_color":  ["Green", "Dark Blue"],
        "food":         ["Red lentils", "Jaggery", "Red fruits"],
        "metal":        "Copper",
        "rudraksha":    "3 Mukhi Rudraksha",
        "life_areas":   ["courage", "property", "siblings", "energy", "surgery"],
    },

    "Mercury": {
        "planet":       "Mercury (Budha)",
        "deity":        "Lord Vishnu / Lord Ganesha",
        "mantra": {
            "beej":     "Om Braam Breem Braum Sah Budhaya Namah",
            "vedic":    "Om Budhaya Namah",
            "gayatri":  "Om Gajadhwajaya Vidmahe Sukha Hasthaya Dheemahi Tanno Budhah Prachodayat",
            "count":    108,
            "day":      "Wednesday"
        },
        "gemstone": {
            "primary":  "Emerald (Panna)",
            "substitute": ["Green Tourmaline", "Peridot", "Green Onyx"],
            "weight":   "4–6 Ratti",
            "metal":    "Gold or Silver",
            "finger":   "Little finger",
            "day":      "Wednesday morning",
            "note":     "Beneficial for students, businessmen, writers"
        },
        "yantra":       "Budha Yantra — energise on Wednesday morning",
        "fasting": {
            "day":      "Wednesday",
            "rules":    "Eat green vegetables; avoid non-veg"
        },
        "charity": [
            "Donate green moong dal, green cloth, books on Wednesdays",
            "Feed green grass to a cow",
            "Donate to educational institutions or libraries"
        ],
        "puja": [
            "Worship Lord Ganesha with durva grass on Wednesdays",
            "Recite Budha Stotra or Budh Ashtottara",
            "Light ghee lamp with green turmeric"
        ],
        "color":        ["Green", "Light Yellow", "Grey"],
        "avoid_color":  ["Red", "Orange"],
        "food":         ["Green moong", "Spinach", "Green vegetables", "Fennel"],
        "metal":        "Bronze or Brass",
        "rudraksha":    "4 Mukhi Rudraksha",
        "life_areas":   ["education", "communication", "business", "intellect", "skin"],
    },

    "Jupiter": {
        "planet":       "Jupiter (Guru / Brihaspati)",
        "deity":        "Lord Brahma / Lord Vishnu / Dakshinamurthy",
        "mantra": {
            "beej":     "Om Graam Greem Graum Sah Gurave Namah",
            "vedic":    "Om Gurave Namah",
            "gayatri":  "Om Vrishabadhwajaya Vidmahe Gruni Hasthaya Dheemahi Tanno Guruh Prachodayat",
            "count":    108,
            "day":      "Thursday"
        },
        "gemstone": {
            "primary":  "Yellow Sapphire (Pukhraj)",
            "substitute": ["Yellow Topaz", "Citrine", "Yellow Beryl"],
            "weight":   "4–6 Ratti",
            "metal":    "Gold",
            "finger":   "Index finger",
            "day":      "Thursday morning",
            "note":     "Best for married life, spirituality, and higher education"
        },
        "yantra":       "Guru Yantra — energise on Thursday morning",
        "fasting": {
            "day":      "Thursday",
            "rules":    "Eat yellow foods; avoid salt in evening meal; eat chickpeas"
        },
        "charity": [
            "Donate yellow cloth, chickpeas, turmeric, gold on Thursdays",
            "Feed banana or sweets to a Brahmin or teacher",
            "Donate to temples, educational trusts, or spiritual organisations"
        ],
        "puja": [
            "Worship Banana tree on Thursday with turmeric water",
            "Recite Brihaspati Stotra or Vishnu Sahasranama",
            "Light ghee lamp with saffron before a Vishnu idol"
        ],
        "color":        ["Yellow", "Gold", "Cream", "Light Orange"],
        "avoid_color":  ["Black", "Dark Grey"],
        "food":         ["Chickpeas", "Banana", "Turmeric milk", "Yellow sweets"],
        "metal":        "Gold",
        "rudraksha":    "5 Mukhi Rudraksha",
        "life_areas":   ["wealth", "children", "marriage", "spirituality", "education", "liver"],
    },

    "Venus": {
        "planet":       "Venus (Shukra)",
        "deity":        "Goddess Lakshmi / Goddess Parvati",
        "mantra": {
            "beej":     "Om Draam Dreem Draum Sah Shukraya Namah",
            "vedic":    "Om Shukraya Namah",
            "gayatri":  "Om Ashwadhwajaya Vidmahe Dhanur Hasthaya Dheemahi Tanno Shukrah Prachodayat",
            "count":    108,
            "day":      "Friday"
        },
        "gemstone": {
            "primary":  "Diamond (Heera)",
            "substitute": ["White Sapphire", "White Zircon", "Opal"],
            "weight":   "1–1.5 Carat",
            "metal":    "Gold or Platinum",
            "finger":   "Middle finger",
            "day":      "Friday morning",
            "note":     "Enhances love, luxury, beauty, and artistic talent"
        },
        "yantra":       "Shukra Yantra — energise on Friday morning",
        "fasting": {
            "day":      "Friday",
            "rules":    "Eat white or colourful foods; offer white sweets to Devi"
        },
        "charity": [
            "Donate white cloth, rice, curd, silver, perfume on Fridays",
            "Feed white sweets to young girls (Kanyadan)",
            "Donate to women's welfare organisations"
        ],
        "puja": [
            "Worship Goddess Lakshmi with white flowers on Fridays",
            "Recite Shukra Stotra or Lakshmi Ashtottara",
            "Light camphor lamp before Devi idol"
        ],
        "color":        ["White", "Pink", "Light Blue", "Cream"],
        "avoid_color":  ["Dark Red", "Brown"],
        "food":         ["Curd", "White rice", "Milk sweets", "White fruits"],
        "metal":        "Silver or Platinum",
        "rudraksha":    "6 Mukhi Rudraksha",
        "life_areas":   ["marriage", "love", "luxury", "beauty", "art", "vehicles", "kidneys"],
    },

    "Saturn": {
        "planet":       "Saturn (Shani)",
        "deity":        "Lord Shani / Lord Hanuman / Lord Yama",
        "mantra": {
            "beej":     "Om Praam Preem Praum Sah Shanaischaraya Namah",
            "vedic":    "Om Shanaischaraya Namah",
            "gayatri":  "Om Kakadwajaya Vidmahe Khadga Hasthaya Dheemahi Tanno Mandah Prachodayat",
            "count":    108,
            "day":      "Saturday"
        },
        "gemstone": {
            "primary":  "Blue Sapphire (Neelam)",
            "substitute": ["Amethyst", "Blue Spinel", "Lapis Lazuli"],
            "weight":   "4–6 Ratti",
            "metal":    "Gold or Panchdhatu",
            "finger":   "Middle finger",
            "day":      "Saturday morning",
            "note":     "CAUTION: Test Blue Sapphire for 3 days before wearing permanently"
        },
        "yantra":       "Shani Yantra — energise on Saturday at sunrise",
        "fasting": {
            "day":      "Saturday",
            "rules":    "Eat only once; sesame-based foods; avoid oil-fried foods"
        },
        "charity": [
            "Donate black sesame, mustard oil, black cloth, iron on Saturdays",
            "Feed black dogs or crows",
            "Donate to the disabled, poor workers, or Shani temples"
        ],
        "puja": [
            "Pour mustard oil on Shani idol or Peepal tree root on Saturdays",
            "Recite Shani Chalisa or Shani Stotra",
            "Light mustard oil lamp at Shani or Hanuman temple on Saturday evenings"
        ],
        "color":        ["Black", "Dark Blue", "Navy", "Dark Grey"],
        "avoid_color":  ["Bright Red", "Gold"],
        "food":         ["Black sesame", "Mustard", "Black urad dal", "Dark foods"],
        "metal":        "Iron or Steel",
        "rudraksha":    "7 Mukhi Rudraksha (14 Mukhi for severe Shani)",
        "life_areas":   ["karma", "discipline", "longevity", "servants", "joints", "delays"],
    },

    "Rahu": {
        "planet":       "Rahu (North Node)",
        "deity":        "Goddess Durga / Goddess Kali / Lord Bhairav",
        "mantra": {
            "beej":     "Om Bhram Bhreem Bhraum Sah Rahave Namah",
            "vedic":    "Om Rahave Namah",
            "gayatri":  "Om Sooksma Rupaya Vidmahe Ugra Rupaya Dheemahi Tanno Rahu Prachodayat",
            "count":    108,
            "day":      "Saturday (or Wednesday)"
        },
        "gemstone": {
            "primary":  "Hessonite Garnet (Gomed)",
            "substitute": ["Zircon", "Spessartite Garnet"],
            "weight":   "6–8 Ratti",
            "metal":    "Panchdhatu or Silver",
            "finger":   "Middle finger",
            "day":      "Saturday evening",
            "note":     "Use only when Rahu is confirmed afflicted in chart"
        },
        "yantra":       "Rahu Yantra — energise on Saturday at dusk",
        "fasting": {
            "day":      "Saturday",
            "rules":    "Observe silence in the morning; eat once; avoid non-veg"
        },
        "charity": [
            "Donate blue/black cloth, mustard oil, coconut on Saturdays",
            "Feed black sesame and jaggery to crows",
            "Donate to leprosy missions or underprivileged communities"
        ],
        "puja": [
            "Perform Rahu Shanti puja or Homa with specific Rahu samidha",
            "Recite Durga Saptashati or Devi Kavach",
            "Donate coconuts at a Bhairav or Kali temple"
        ],
        "color":        ["Navy Blue", "Dark Maroon", "Smoky Grey"],
        "avoid_color":  ["Bright Yellow", "Gold"],
        "food":         ["Coconut", "Black sesame", "Black gram"],
        "metal":        "Lead or Panchdhatu",
        "rudraksha":    "8 Mukhi Rudraksha",
        "life_areas":   ["foreign travel", "technology", "confusion", "sudden events", "smoke", "poison"],
    },

    "Ketu": {
        "planet":       "Ketu (South Node)",
        "deity":        "Lord Ganesha / Lord Bhairav / Goddess Kali",
        "mantra": {
            "beej":     "Om Sraam Sreem Sraum Sah Ketave Namah",
            "vedic":    "Om Ketave Namah",
            "gayatri":  "Om Ashwadhwajaya Vidmahe Soola Hasthaya Dheemahi Tanno Ketu Prachodayat",
            "count":    108,
            "day":      "Tuesday (or Thursday)"
        },
        "gemstone": {
            "primary":  "Cat's Eye (Lehsunia / Vaidurya)",
            "substitute": ["Tiger's Eye", "Chrysoberyl"],
            "weight":   "5–7 Ratti",
            "metal":    "Panchdhatu or Gold",
            "finger":   "Middle finger",
            "day":      "Tuesday morning",
            "note":     "Use only when Ketu is afflicted — can cause sudden changes"
        },
        "yantra":       "Ketu Yantra — energise on Tuesday or Thursday",
        "fasting": {
            "day":      "Tuesday",
            "rules":    "Eat only once; red/saffron foods; no non-veg"
        },
        "charity": [
            "Donate blankets, multicoloured cloth, sesame on Tuesdays",
            "Feed stray dogs",
            "Donate to spiritual ashrams or animal shelters"
        ],
        "puja": [
            "Perform Ketu Shanti puja or Ganesha puja",
            "Recite Ganesha Atharvashirsha",
            "Offer durva grass and modak to Ganesha on Tuesdays"
        ],
        "color":        ["Multicolour", "Smoky", "Ash Grey", "Saffron"],
        "avoid_color":  ["Bright Green"],
        "food":         ["Sesame", "Black gram", "Coconut"],
        "metal":        "Iron or Panchdhatu",
        "rudraksha":    "9 Mukhi Rudraksha",
        "life_areas":   ["spirituality", "moksha", "accidents", "hidden enemies", "wounds"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# DOSHA REMEDIES
# ─────────────────────────────────────────────────────────────────────────────

DOSHA_REMEDIES = {
    "mangal_dosha": {
        "dosha":        "Mangal Dosha (Kuja Dosha)",
        "description":  "Mars placed in 1st, 2nd, 4th, 7th, 8th, or 12th house",
        "impact":       "Delays in marriage, marital discord, health issues for spouse",
        "severity_levels": {
            "mild":   "Mars in 1st or 4th house",
            "moderate": "Mars in 2nd or 12th house",
            "severe": "Mars in 7th or 8th house"
        },
        "mantra":       "Om Angarakaya Namah (108 times on Tuesdays for 40 days)",
        "puja": [
            "Perform Mangal Shanti Puja or Kuja Dosha Nivarana Puja",
            "Visit Mangalnath Temple (Ujjain) or any Hanuman temple on Tuesdays",
            "Recite Hanuman Chalisa daily"
        ],
        "ritual": [
            "Kumbh Vivah (marry a banana tree, peepal tree, or Vishnu idol before human marriage)",
            "Perform Mangal Graha Homa on a Tuesday",
            "Offer red flowers to Hanuman on 11 consecutive Tuesdays"
        ],
        "charity":      "Donate red coral, red cloth, masoor dal, copper on Tuesdays",
        "gemstone":     "Red Coral (Moonga) in copper/gold ring on right ring finger",
        "fasting":      "Fast on Tuesdays for 21 consecutive weeks",
        "rudraksha":    "3 Mukhi Rudraksha worn on Tuesday",
        "cancellation": [
            "Mangal Dosha is cancelled if Mars is in its own sign (Aries/Scorpio)",
            "Cancelled if Mars is exalted (Capricorn)",
            "Cancelled if both partners have Mangal Dosha",
            "Cancelled if Jupiter aspects the 7th house strongly"
        ],
    },

    "kaal_sarp_dosha": {
        "dosha":        "Kaal Sarp Dosha",
        "description":  "All 7 planets hemmed between Rahu and Ketu in the birth chart",
        "impact":       "Repeated failures, delays, ancestral problems, fear, mental unrest",
        "types":        [
            "Anant Kaal Sarp (Rahu in 1st)",
            "Kulik Kaal Sarp (Rahu in 2nd)",
            "Vasuki Kaal Sarp (Rahu in 3rd)",
            "Shankhpal Kaal Sarp (Rahu in 4th)",
            "Padma Kaal Sarp (Rahu in 5th)",
            "Mahapadma Kaal Sarp (Rahu in 6th)",
            "Takshak Kaal Sarp (Rahu in 7th)",
            "Karkotak Kaal Sarp (Rahu in 8th)",
            "Shankhachur Kaal Sarp (Rahu in 9th)",
            "Ghatak Kaal Sarp (Rahu in 10th)",
            "Vishdhar Kaal Sarp (Rahu in 11th)",
            "Sheshnaag Kaal Sarp (Rahu in 12th)",
        ],
        "mantra":       "Om Namo Bhagavate Vasudevaya (108 times) + Maha Mrityunjaya (11 times)",
        "puja": [
            "Kaal Sarp Dosha Nivaran Puja at Trimbakeshwar (Nashik) — most effective",
            "Nag Panchami puja — worship snake idols with milk",
            "Perform Rudrabhishek on a Monday"
        ],
        "ritual": [
            "Fast on Nag Panchami and offer milk to a snake idol",
            "Feed milk to a live snake (at a snake park or controlled environment)",
            "Plant a pair of Nag-Nagini idols at home and worship daily"
        ],
        "charity":      "Donate silver snake idols, blue/black cloth, sesame on Saturdays",
        "gemstone":     "Hessonite (Gomed) + Cat's Eye (Lehsunia) together after chart analysis",
        "fasting":      "Fast on both Saturday and Tuesday for 18 weeks",
        "rudraksha":    "8 Mukhi + 9 Mukhi Rudraksha combination",
    },

    "pitru_dosha": {
        "dosha":        "Pitru Dosha (Ancestral Debt)",
        "description":  "Sun, Moon, or Rahu in 9th house, or afflicted 9th lord; indicates unpaid ancestral debt",
        "impact":       "Delayed marriage, no children, chronic illness, repeated misfortune",
        "mantra":       "Om Pitrubhyo Namah (108 times) + Gayatri Mantra",
        "puja": [
            "Perform Pitru Tarpan (water offering to ancestors) on every Amavasya (new moon)",
            "Perform Shraddha ceremonies on the death anniversary (Tithi) of ancestors",
            "Gaya Shraddha Puja at Gaya (Bihar) — most powerful remedy"
        ],
        "ritual": [
            "Offer Pind Daan at Gaya, Prayagraj, or Varanasi",
            "Feed crows every day — crows represent ancestors in Vedic tradition",
            "Feed Brahmins on Amavasya with special pitru food (cooked rice, sesame, black urad)"
        ],
        "charity": [
            "Donate food, clothes, and money to the elderly and underprivileged",
            "Donate a cow (Go Daan) in ancestor's name",
            "Plant Peepal tree and water it on Saturdays"
        ],
        "gemstone":     "Not applicable — remedy is ritual-based",
        "fasting":      "Fast on Amavasya (no-moon day) every month",
        "rudraksha":    "11 Mukhi Rudraksha for ancestral blessings",
    },

    "sade_sati": {
        "dosha":        "Shani Sade Sati (7.5 years of Saturn)",
        "description":  "Saturn transiting through the 12th, 1st, and 2nd house from natal Moon — 7.5 years total",
        "phases": {
            "rising":   "Saturn in 12th from Moon — losses, expenses, isolation",
            "peak":     "Saturn in 1st (Moon sign) — maximum pressure, health, personal challenges",
            "setting":  "Saturn in 2nd from Moon — financial stress, family issues"
        },
        "impact":       "Career setbacks, health issues, mental stress, financial pressure",
        "mantra":       "Om Sham Shanaischaraya Namah (108 times on Saturdays)",
        "puja": [
            "Perform Shani Shanti Puja on Saturdays",
            "Recite Shani Chalisa every Saturday",
            "Visit Shani temple and pour mustard oil on idol"
        ],
        "ritual": [
            "Light a mustard oil lamp under a Peepal tree on Saturday evenings",
            "Observe Shani Vrat (fast) on 11 or 19 consecutive Saturdays",
            "Worship Lord Hanuman on Tuesdays AND Saturdays"
        ],
        "charity": [
            "Donate black sesame, iron items, black cloth, mustard oil on Saturdays",
            "Feed black dogs and crows",
            "Donate to the disabled, labourers, or poor farmers"
        ],
        "gemstone":     "Blue Sapphire (test first!) or Amethyst as substitute",
        "fasting":      "Fast on Saturdays — eat sesame-based food only once",
        "rudraksha":    "7 Mukhi Rudraksha or 14 Mukhi Rudraksha for Sade Sati relief",
    },

    "guru_chandal_dosha": {
        "dosha":        "Guru Chandal Dosha",
        "description":  "Jupiter conjunct or aspected by Rahu in the birth chart",
        "impact":       "Poor judgment, unethical guidance, troubled teacher/guru relationships, false beliefs",
        "mantra":       "Om Graam Greem Graum Sah Gurave Namah (108 times on Thursdays)",
        "puja": [
            "Guru Chandal Dosha Nivaran Puja on a Thursday",
            "Perform Brihaspati Homa",
            "Worship Lord Vishnu with tulsi and yellow flowers on Thursdays"
        ],
        "ritual": [
            "Serve and respect a genuine teacher or spiritual guru",
            "Read Vishnu Sahasranama every Thursday",
            "Donate books, knowledge, and educational material to the needy"
        ],
        "charity":      "Donate yellow cloth, chickpeas, turmeric, gold on Thursdays",
        "gemstone":     "Yellow Sapphire (Pukhraj) in gold ring on right index finger",
        "fasting":      "Fast on Thursdays for 16 consecutive weeks",
        "rudraksha":    "5 Mukhi Rudraksha (Jupiter) to counteract Rahu influence",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# LIFE AREA REMEDIES
# ─────────────────────────────────────────────────────────────────────────────

LIFE_AREA_REMEDIES = {
    "health": {
        "area":         "Health & Wellbeing",
        "ruling_planets": ["Sun", "Moon", "Mars"],
        "general": [
            "Recite Mahamrityunjaya Mantra (Om Tryambakam...) 108 times daily",
            "Offer water to Sun at sunrise daily (Surya Arghya)",
            "Wear 3 Mukhi Rudraksha for Mars-related health issues",
            "Wear 2 Mukhi Rudraksha for Moon-related mental health",
        ],
        "mantra":       "Om Tryambakam Yajamahe Sugandhim Pushtivardhanam Urvarukamiva Bandhanan Mrityor Mukshiya Maamritat",
        "puja":         "Dhanvantari Puja on Dhanteras or Thursday for healing",
        "charity":      "Donate medicines, blankets to hospitals; feed the sick",
        "fasting":      "Fast on Sunday for Sun-related health, Monday for mental peace",
        "gemstone":     "Red Coral for physical vitality; Pearl for mental health",
        "color":        ["Saffron", "White", "Red"],
        "food":         ["Tulsi leaves in water daily", "Turmeric milk", "Fasting once a week"],
    },
    "wealth": {
        "area":         "Wealth & Finance",
        "ruling_planets": ["Jupiter", "Venus", "Mercury"],
        "general": [
            "Recite Shree Sukta (Lakshmi Sukta) daily — especially on Fridays",
            "Keep a Shree Yantra in home/office facing East or North",
            "Offer yellow flowers to Lord Vishnu on Thursdays",
            "Light a ghee lamp before Goddess Lakshmi on Fridays",
        ],
        "mantra":       "Om Shreem Hreem Kleem Maha Lakshmyai Namah (108 times on Fridays)",
        "puja":         "Lakshmi Puja every Friday, Kubera Puja on Thursdays",
        "charity":      "Donate food/money on Thursdays and Fridays; feed Brahmins",
        "fasting":      "Fast on Thursday for Jupiter blessings, Friday for Venus/Lakshmi",
        "gemstone":     "Yellow Sapphire for Jupiter; Diamond/White Sapphire for Venus",
        "color":        ["Yellow", "Gold", "Green"],
        "food":         ["Saffron milk on Thursdays", "Yellow sweets on Fridays"],
    },
    "relationship": {
        "area":         "Relationships & Marriage",
        "ruling_planets": ["Venus", "Jupiter", "Moon"],
        "general": [
            "Recite Gauri-Shankar mantra for harmonious relationships",
            "Worship Lord Shiva and Parvati together on Mondays",
            "Perform Rudrabhishek for marriage blessings",
            "Offer white flowers to Goddess Parvati on Mondays",
        ],
        "mantra":       "Om Gaurishankaraya Namah (108 times on Mondays)",
        "puja":         "Swayamvara Parvathi Puja for marriage delays; Rudrabhishek for marital harmony",
        "charity":      "Donate white cloth, milk, rice to a married couple or Brahmin family",
        "fasting":      "Fast on Monday for Moon; Friday for Venus blessings in love",
        "gemstone":     "Pearl for emotional bonding; Diamond for love and marriage",
        "color":        ["White", "Pink", "Light Blue"],
        "food":         ["White sweets on Mondays", "Curd and sugar before leaving home"],
    },
    "career": {
        "area":         "Career & Profession",
        "ruling_planets": ["Sun", "Saturn", "Mercury", "Jupiter"],
        "general": [
            "Recite Surya Ashtottara for career growth",
            "Offer water to Sun at sunrise on Sundays",
            "Worship Lord Ganesha before starting any new work",
            "Keep a Surya Yantra or Guru Yantra at your workplace",
        ],
        "mantra":       "Om Suryaya Namah (108 times on Sundays) for authority; Om Shanaischaraya Namah for discipline",
        "puja":         "Saraswati Puja for intellectual careers; Surya Puja for government/leadership",
        "charity":      "Donate on Sundays for Sun; Saturdays for Saturn; feed workers/labourers",
        "fasting":      "Fast on Sunday for Sun-related careers (government, politics, management)",
        "gemstone":     "Ruby for Sun (leadership/govt); Blue Sapphire for Saturn (service/hard work)",
        "color":        ["Orange", "Gold", "Dark Blue"],
        "food":         ["Wheat on Sundays", "Jaggery on Sundays"],
    },
    "education": {
        "area":         "Education & Learning",
        "ruling_planets": ["Mercury", "Jupiter"],
        "general": [
            "Worship Goddess Saraswati daily — especially on Wednesdays",
            "Recite Saraswati mantra before studying",
            "Keep a Budha Yantra or Saraswati Yantra at the study desk",
            "Offer durva grass to Lord Ganesha on Wednesdays",
        ],
        "mantra":       "Om Aim Saraswatyai Namah (108 times before studying)",
        "puja":         "Saraswati Puja on Vasant Panchami; Vidyarambha Puja for new academic year",
        "charity":      "Donate books, stationery, pens on Wednesdays; donate to poor students",
        "fasting":      "Fast on Wednesday for Mercury blessings in education",
        "gemstone":     "Emerald for Mercury; Yellow Sapphire for Jupiter",
        "color":        ["Green", "Yellow", "White"],
        "food":         ["Green moong dal on Wednesdays", "Saffron milk for memory"],
    },
    "legal": {
        "area":         "Legal Matters & Court Cases",
        "ruling_planets": ["Saturn", "Rahu", "Sun"],
        "general": [
            "Recite Shani Chalisa every Saturday",
            "Light mustard oil lamp at Shani temple on Saturdays",
            "Perform Bagalamukhi Puja for legal victory",
            "Recite Bagalamukhi Mantra for silencing opponents",
        ],
        "mantra":       "Om Hleem Bagalamukhi Sarva Dushtanam Vacham Mukham Padam Stambhaya Jivham Keelaya Keelaya Budham Vinashaya Hleem Om Swaha (108 times)",
        "puja":         "Bagalamukhi Puja for court victory; Shani Shanti for Saturn-caused delays",
        "charity":      "Donate black sesame, iron, mustard oil to the poor on Saturdays",
        "fasting":      "Fast on Saturday for Saturn; offer mustard oil to Shani idol",
        "gemstone":     "Blue Sapphire (Saturn) with caution; Hessonite for Rahu if involved",
        "color":        ["Yellow", "Saffron", "Blue"],
        "food":         ["Sesame-based food on Saturdays"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — swisseph calculations
# ─────────────────────────────────────────────────────────────────────────────

def _parse_dt(value):
    if value is None:
        return None
    if hasattr(value, "year") and hasattr(value, "hour"):
        return value
    value = str(value).strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: '{value}'")


def _parse_date(value):
    if value is None:
        return None
    if hasattr(value, "year"):
        return value
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: '{value}'")


def _parse_time(value):
    if value is None:
        return None
    if hasattr(value, "hour"):
        return value
    value = str(value).strip()
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse time: '{value}'")


def _to_jd(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ut = dt.utctimetuple()
    hour_frac = ut.tm_hour + ut.tm_min / 60.0 + ut.tm_sec / 3600.0
    return swe.julday(ut.tm_year, ut.tm_mon, ut.tm_mday, hour_frac)


def _planet_positions(jd: float) -> dict:
    """Return sidereal longitude for all 9 grahas."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    positions = {}
    for name, pid in SWE_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, flags)
        positions[name] = result[0]
    # Rahu (mean node)
    rahu_result, _ = swe.calc_ut(jd, SWE_RAHU, flags)
    positions["Rahu"] = rahu_result[0]
    positions["Ketu"] = (rahu_result[0] + 180) % 360
    return positions


def _rashi_from_lon(lon: float) -> str:
    return RASHIS[int(lon / 30) % 12]


def _house_from_lagna(planet_lon: float, lagna_lon: float) -> int:
    diff = (planet_lon - lagna_lon) % 360
    return int(diff / 30) + 1


def _is_planet_weak(planet: str, rashi: str) -> tuple:
    """
    Returns (is_weak: bool, reason: str)
    Weak = debilitated or in enemy sign
    """
    if rashi == DEBILITATION.get(planet):
        return True, f"Debilitated in {rashi}"
    if rashi in ENEMY_SIGNS.get(planet, []):
        return True, f"In enemy sign {rashi}"
    return False, ""


def _detect_kaal_sarp(positions: dict, lagna_lon: float) -> tuple:
    """
    Returns (has_kaal_sarp: bool, type_name: str|None)
    Checks if all 7 planets are between Rahu and Ketu (hemmed).
    """
    rahu_lon = positions["Rahu"]
    ketu_lon = positions["Ketu"]

    def between_rahu_ketu(lon):
        # Check if lon falls in the arc from Rahu to Ketu (going forward)
        arc = (ketu_lon - rahu_lon) % 360
        dist = (lon - rahu_lon) % 360
        return dist < arc

    planets_to_check = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    all_hemmed = all(between_rahu_ketu(positions[p]) for p in planets_to_check)

    if not all_hemmed:
        return False, None

    rahu_house = _house_from_lagna(rahu_lon, lagna_lon)
    type_map = {
        1: "Anant", 2: "Kulik", 3: "Vasuki", 4: "Shankhpal",
        5: "Padma", 6: "Mahapadma", 7: "Takshak", 8: "Karkotak",
        9: "Shankhachur", 10: "Ghatak", 11: "Vishdhar", 12: "Sheshnaag"
    }
    ksd_type = f"{type_map.get(rahu_house, 'Unknown')} Kaal Sarp Dosha (Rahu in house {rahu_house})"
    return True, ksd_type


def _detect_mangal_dosha(positions: dict, lagna_lon: float) -> tuple:
    """
    Returns (has_mangal_dosha: bool, severity: str, house: int)
    Mangal Dosha houses: 1, 2, 4, 7, 8, 12
    """
    mars_house = _house_from_lagna(positions["Mars"], lagna_lon)
    dosha_houses = {1: "mild", 2: "moderate", 4: "mild", 7: "severe", 8: "severe", 12: "moderate"}
    if mars_house in dosha_houses:
        return True, dosha_houses[mars_house], mars_house
    return False, None, mars_house


def _detect_guru_chandal(positions: dict) -> bool:
    """Jupiter and Rahu in same sign."""
    jup_rashi = _rashi_from_lon(positions["Jupiter"])
    rahu_rashi = _rashi_from_lon(positions["Rahu"])
    return jup_rashi == rahu_rashi


def _sade_sati_status(natal_moon_rashi: str, transit_positions: dict) -> tuple:
    """
    Returns (in_sade_sati: bool, phase: str|None)
    Checks current Saturn transit relative to natal Moon sign.
    """
    natal_moon_idx   = RASHIS.index(natal_moon_rashi)
    saturn_rashi     = _rashi_from_lon(transit_positions["Saturn"])
    saturn_rashi_idx = RASHIS.index(saturn_rashi)

    diff = (saturn_rashi_idx - natal_moon_idx) % 12
    if diff == 11:
        return True, "rising"    # Saturn in 12th from Moon
    elif diff == 0:
        return True, "peak"      # Saturn on Moon sign
    elif diff == 1:
        return True, "setting"   # Saturn in 2nd from Moon
    return False, None


# ─────────────────────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def get_remedies(
    dob=None,
    tob=None,
    current_dt=None,
    planet=None,
    life_area=None,
    dosha=None,
    janma_rashi=None,
):
    """
    Get comprehensive astrology remedies.

    Parameters
    ----------
    dob        : str|date     – date of birth (YYYY-MM-DD or DD-MM-YYYY)
    tob        : str|time     – time of birth (HH:MM or HH:MM:SS)
    current_dt : str|datetime – transit date for analysis (default = today's date, UTC)
    planet     : str          – specific planet remedy e.g. "Saturn", "Rahu", "Venus"
    life_area  : str          – "health" | "wealth" | "relationship" | "career" | "education" | "legal"
    dosha      : str          – "mangal_dosha" | "kaal_sarp_dosha" | "pitru_dosha" |
                                "sade_sati" | "guru_chandal_dosha"
    janma_rashi: str          – override Moon sign (used if no birth data)

    Returns
    -------
    dict with status, status_code, response
    """

    result = {
        "planet_remedies":    [],
        "dosha_remedies":     [],
        "life_area_remedies": [],
        "weak_planets":       [],
        "active_doshas":      [],
        "transit_alerts":     [],
    }

    # ── Parse inputs ────────────────────────────────────────────────────────
    dob = _parse_date(dob)
    tob = _parse_time(tob)
    if current_dt is None:
        current_dt = datetime.now(timezone.utc)   # defaults to TODAY automatically
    else:
        current_dt = _parse_dt(current_dt)

    birth_data_available = dob is not None and tob is not None

    # ── Current transit positions ────────────────────────────────────────────
    transit_jd        = _to_jd(current_dt)
    transit_positions = _planet_positions(transit_jd)

    # ── Birth chart positions ────────────────────────────────────────────────
    natal_positions = None
    lagna_lon       = None
    natal_moon_rashi = janma_rashi

    if birth_data_available:
        birth_dt = datetime(
            dob.year, dob.month, dob.day,
            tob.hour, tob.minute, tob.second,
            tzinfo=getattr(tob, "tzinfo", None)
        )
        natal_jd        = _to_jd(birth_dt)
        natal_positions = _planet_positions(natal_jd)

        # Lagna (Ascendant) via ARMC approximation (simplified):
        # Use Sun position offset for a rough lagna — for precise lagna, house system needed
        lagna_lon = natal_positions["Sun"]  # simplified; replace with proper Ascendant if needed

        if natal_moon_rashi is None:
            natal_moon_rashi = _rashi_from_lon(natal_positions["Moon"])

        # ── Detect weak planets ───────────────────────────────────────────
        for pname, plon in natal_positions.items():
            prashi = _rashi_from_lon(plon)
            weak, reason = _is_planet_weak(pname, prashi)
            if weak:
                result["weak_planets"].append({
                    "planet":  pname,
                    "rashi":   prashi,
                    "reason":  reason,
                    "remedy":  PLANET_REMEDIES.get(pname, {}),
                })

        # ── Auto-detect doshas from birth chart ───────────────────────────
        # Mangal Dosha
        has_md, md_severity, mars_house = _detect_mangal_dosha(natal_positions, lagna_lon)
        if has_md:
            result["active_doshas"].append({
                "dosha":    "mangal_dosha",
                "severity": md_severity,
                "detail":   f"Mars in house {mars_house}",
                "remedy":   DOSHA_REMEDIES["mangal_dosha"],
            })

        # Kaal Sarp Dosha
        has_ksd, ksd_type = _detect_kaal_sarp(natal_positions, lagna_lon)
        if has_ksd:
            result["active_doshas"].append({
                "dosha":  "kaal_sarp_dosha",
                "detail": ksd_type,
                "remedy": DOSHA_REMEDIES["kaal_sarp_dosha"],
            })

        # Guru Chandal Dosha
        if _detect_guru_chandal(natal_positions):
            result["active_doshas"].append({
                "dosha":  "guru_chandal_dosha",
                "detail": "Jupiter conjunct Rahu in birth chart",
                "remedy": DOSHA_REMEDIES["guru_chandal_dosha"],
            })

    # ── Transit alerts ───────────────────────────────────────────────────────
    if natal_moon_rashi:
        in_ss, ss_phase = _sade_sati_status(natal_moon_rashi, transit_positions)
        if in_ss:
            result["transit_alerts"].append({
                "alert":  "Shani Sade Sati Active",
                "phase":  ss_phase,
                "detail": DOSHA_REMEDIES["sade_sati"]["phases"].get(ss_phase, ""),
                "remedy": DOSHA_REMEDIES["sade_sati"],
            })

    # ── Specific planet remedy request ───────────────────────────────────────
    if planet:
        planet_key = planet.strip().capitalize()
        if planet_key in PLANET_REMEDIES:
            result["planet_remedies"].append(PLANET_REMEDIES[planet_key])
        else:
            result["planet_remedies"].append({
                "error": f"Unknown planet '{planet}'. Valid: {list(PLANET_REMEDIES.keys())}"
            })

    # ── Specific dosha remedy request ────────────────────────────────────────
    if dosha:
        dosha_key = dosha.strip().lower()
        if dosha_key in DOSHA_REMEDIES:
            result["dosha_remedies"].append(DOSHA_REMEDIES[dosha_key])
        else:
            result["dosha_remedies"].append({
                "error": f"Unknown dosha '{dosha}'. Valid: {list(DOSHA_REMEDIES.keys())}"
            })

    # ── Life area remedy request ─────────────────────────────────────────────
    if life_area:
        area_key = life_area.strip().lower()
        if area_key in LIFE_AREA_REMEDIES:
            result["life_area_remedies"].append(LIFE_AREA_REMEDIES[area_key])
        else:
            result["life_area_remedies"].append({
                "error": f"Unknown life_area '{life_area}'. Valid: {list(LIFE_AREA_REMEDIES.keys())}"
            })

    # ── Summary ──────────────────────────────────────────────────────────────
    total_issues = (
        len(result["weak_planets"]) +
        len(result["active_doshas"]) +
        len(result["transit_alerts"])
    )

    if total_issues == 0 and not any([planet, dosha, life_area]):
        summary = "No major afflictions detected. General daily remedies recommended for overall wellbeing."
    elif total_issues > 0:
        issue_names = (
            [w["planet"] + " (weak)" for w in result["weak_planets"]] +
            [d["dosha"] for d in result["active_doshas"]] +
            [t["alert"] for t in result["transit_alerts"]]
        )
        summary = f"{total_issues} issue(s) detected: {', '.join(issue_names)}. Perform listed remedies consistently."
    else:
        summary = "Remedies provided as requested."

    return {
        "status":      "success",
        "status_code": "200",
        "response": {
            "summary":             summary,
            "natal_moon_rashi":    natal_moon_rashi,
            "birth_chart_used":    birth_data_available,
            "total_issues_found":  total_issues,
            "result":              result,
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # 1. Full birth chart analysis — auto-detects weak planets + doshas
    r1 = get_remedies(
        dob="1990-05-15",
        tob="10:30:00",
    )
    print("── Full Birth Chart Analysis ──")
    print(json.dumps(r1, indent=2, default=str))

    print()

    # 2. Specific planet remedy only
    r2 = get_remedies(planet="Saturn")
    print("── Saturn Remedies ──")
    print(json.dumps(r2, indent=2, default=str))

    print()

    # 3. Life area remedy only
    r3 = get_remedies(life_area="wealth")
    print("── Wealth Remedies ──")
    print(json.dumps(r3, indent=2, default=str))

    print()

    # 4. Specific dosha remedy
    r4 = get_remedies(dosha="kaal_sarp_dosha")
    print("── Kaal Sarp Dosha Remedies ──")
    print(json.dumps(r4, indent=2, default=str))

    print()

    # 5. Transit-only check (no birth data) with known Moon sign
    r5 = get_remedies(janma_rashi="Capricorn", current_dt="2025-07-19 08:00:00")
    print("── Transit Check (Capricorn Moon) ──")
    print(json.dumps(r5, indent=2, default=str))