"""
catout_ears_keys.py

Vocabulary and logic for specific catears and keys.

The logic here comes into play only after the "etd_text" has already
been parsed into keys (catear or normal) and their values.
"""

VALID_CATEARS = [
    "home",
    "away",
    "miss",
    "sens",
    "cw",
    "note",
    "np",
    "role" ]


VALID_KEYS = [
    "contrib",
    "air",
    "rec",
    "copyright-year",
    "copyright-owner",
    "copr", 
    "date",
    "prog-title",
    "series-title",
    "ep-title", 
    "title",
    "ep-no",
    "dir",
    "prod",
    "cam"
]

VALID_ROLES = [
]
