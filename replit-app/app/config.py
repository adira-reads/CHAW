"""
Application Configuration

Handles all configuration settings via environment variables.
Uses Pydantic Settings for validation and type coercion.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "UFLI Tracking System"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ufli_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]

    # Site defaults
    DEFAULT_SITE_NAME: str = "UFLI School"
    DEFAULT_TIMEZONE: str = "America/New_York"

    # Feature flags
    FEATURE_TUTORING: bool = True
    FEATURE_PACING: bool = True
    FEATURE_PARENT_REPORTS: bool = False

    # Optional integrations
    MONDAY_API_KEY: Optional[str] = None
    MONDAY_BOARD_ID: Optional[str] = None

    # Google Sheets import (for migration)
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()


# UFLI Curriculum Constants
# These are fixed values that don't change

TOTAL_LESSONS = 128

# Review lessons (cannot be used for initial assessment scoring)
REVIEW_LESSONS = [
    35, 36, 37, 39, 40, 41, 49, 53, 57, 59, 62, 71, 76, 79, 83, 88, 92, 97, 102, 104, 105, 106, 128
]

# Foundational lessons (1-34)
FOUNDATIONAL_LESSONS = list(range(1, 35))

# Grade-specific lesson requirements
GRADE_LESSON_CONFIG = {
    "PreK": {
        "min_lessons": list(range(1, 27)),  # Letters a-z
        "benchmark_denominator": 26,
        "is_letter_based": True
    },
    "KG": {
        "min_lessons": list(range(1, 35)),  # Foundational only
        "benchmark_denominator": 34,
        "is_letter_based": False
    },
    "G1": {
        "min_lessons": list(range(1, 35)) + list(range(42, 54)),  # Foundational + Digraphs
        "current_year_lessons": list(range(42, 54)),
        "benchmark_denominator": 44,
        "is_letter_based": False
    },
    "G2": {
        "min_lessons": list(range(1, 35)) + list(range(42, 63)),  # Through VCE
        "current_year_lessons": list(range(54, 63)),
        "benchmark_denominator": 56,
        "is_letter_based": False
    },
    "G3": {
        "min_lessons": list(range(1, 35)) + list(range(42, 63)),
        "current_year_lessons": list(range(63, 84)),
        "benchmark_denominator": 56,
        "is_letter_based": False
    },
    "G4": {
        "min_lessons": list(range(1, 35)) + list(range(42, 111)),
        "current_year_lessons": list(range(84, 111)),
        "benchmark_denominator": 103,
        "is_letter_based": False
    },
    "G5": {
        "min_lessons": list(range(1, 35)) + list(range(42, 111)),
        "current_year_lessons": list(range(84, 111)),
        "benchmark_denominator": 103,
        "is_letter_based": False
    },
    "G6": {
        "min_lessons": list(range(1, 35)) + list(range(42, 111)),
        "current_year_lessons": list(range(84, 129)),
        "benchmark_denominator": 103,
        "is_letter_based": False
    },
    "G7": {
        "min_lessons": list(range(1, 35)) + list(range(42, 111)),
        "current_year_lessons": list(range(84, 129)),
        "benchmark_denominator": 103,
        "is_letter_based": False
    },
    "G8": {
        "min_lessons": list(range(1, 35)) + list(range(42, 111)),
        "current_year_lessons": list(range(84, 129)),
        "benchmark_denominator": 103,
        "is_letter_based": False
    },
}

# Skill sections with lesson ranges
SKILL_SECTIONS = [
    {"id": 1, "name": "Single Consonants & Short Vowels", "lessons": list(range(1, 35))},
    {"id": 2, "name": "Blends", "lessons": [25, 27]},
    {"id": 3, "name": "Alphabet Review", "lessons": list(range(35, 42))},
    {"id": 4, "name": "Digraphs", "lessons": list(range(42, 54))},
    {"id": 5, "name": "VCE (Vowel-Consonant-E)", "lessons": list(range(54, 63))},
    {"id": 6, "name": "Reading Longer Words", "lessons": list(range(63, 69))},
    {"id": 7, "name": "Ending Spelling Patterns", "lessons": list(range(69, 77))},
    {"id": 8, "name": "R-Controlled Vowels", "lessons": list(range(77, 84))},
    {"id": 9, "name": "Long Vowel Teams", "lessons": list(range(84, 89))},
    {"id": 10, "name": "Other Vowel Teams", "lessons": list(range(89, 95))},
    {"id": 11, "name": "Diphthongs", "lessons": list(range(95, 98))},
    {"id": 12, "name": "Silent Letters", "lessons": [98]},
    {"id": 13, "name": "Suffixes & Prefixes", "lessons": list(range(99, 107))},
    {"id": 14, "name": "Suffix Spelling Changes", "lessons": list(range(107, 111))},
    {"id": 15, "name": "Low Frequency Spellings", "lessons": list(range(111, 119))},
    {"id": 16, "name": "Additional Affixes", "lessons": list(range(119, 127))},
    {"id": 17, "name": "Affixes Review 2", "lessons": [127, 128]},
]

# UFLI Lesson names (abbreviated)
LESSON_NAMES = {
    1: "a/ā/",
    2: "m",
    3: "t",
    4: "s",
    5: "i/ī/",
    6: "f",
    7: "d",
    8: "r",
    9: "o/ō/",
    10: "g",
    11: "l",
    12: "h",
    13: "u/ū/",
    14: "c",
    15: "b",
    16: "n",
    17: "k",
    18: "e/ē/",
    19: "v",
    20: "y",
    21: "w",
    22: "j",
    23: "p",
    24: "x",
    25: "blends (initial)",
    26: "z",
    27: "blends (final)",
    28: "qu",
    29: "-ck",
    30: "-ll, -ss",
    31: "-zz, -ff",
    32: "-ng",
    33: "-nk",
    34: "Review 1-33",
    35: "Review a",
    36: "Review i",
    37: "Review o",
    38: "Review u",
    39: "Review e",
    40: "Review 35-39",
    41: "Review all vowels",
    42: "ch",
    43: "sh",
    44: "th",
    45: "wh",
    46: "-tch",
    47: "ph",
    48: "wr",
    49: "Review digraphs",
    50: "kn",
    51: "gn",
    52: "mb",
    53: "Review 50-52",
    54: "a_e",
    55: "i_e",
    56: "o_e",
    57: "Review 54-56",
    58: "u_e",
    59: "Review 54-58",
    60: "e_e",
    61: "Soft c",
    62: "Soft g",
    63: "Compound words",
    64: "Syllable division (VC/CV)",
    65: "Syllable division (V/CV)",
    66: "Syllable division (VC/V)",
    67: "Syllable division (review)",
    68: "Open syllables",
    69: "-ed (/ed/)",
    70: "-ed (/d/)",
    71: "-ed (/t/)",
    72: "-ing",
    73: "-er, -est",
    74: "-s, -es",
    75: "-ful, -less",
    76: "Review suffixes",
    77: "ar",
    78: "or",
    79: "Review ar, or",
    80: "er",
    81: "ir",
    82: "ur",
    83: "Review er, ir, ur",
    84: "ai",
    85: "ay",
    86: "ee",
    87: "ea",
    88: "Review vowel teams",
    89: "igh",
    90: "ie",
    91: "oa",
    92: "ow (/ō/)",
    93: "ew",
    94: "ue",
    95: "oi",
    96: "oy",
    97: "Review diphthongs",
    98: "Silent letters",
    99: "Prefixes un-, re-",
    100: "Prefixes pre-, mis-",
    101: "Prefixes dis-, non-",
    102: "Review prefixes",
    103: "Suffixes -ly, -y",
    104: "Suffixes -ment, -ness",
    105: "Suffixes -able, -ible",
    106: "Review suffixes 2",
    107: "Doubling rule",
    108: "Drop e rule",
    109: "Change y rule",
    110: "Review spelling rules",
    111: "oo (/o͞o/)",
    112: "oo (/o͝o/)",
    113: "ou",
    114: "ow (/ou/)",
    115: "au, aw",
    116: "al, all",
    117: "wa, qua",
    118: "Review 111-117",
    119: "-tion",
    120: "-sion",
    121: "-ture, -sure",
    122: "-cial, -tial",
    123: "-ous, -eous",
    124: "-ible, -able (advanced)",
    125: "Greek roots",
    126: "Latin roots",
    127: "Review affixes 1",
    128: "Review affixes 2",
}
