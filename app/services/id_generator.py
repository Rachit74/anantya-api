"""
Unique ID Generator Service

This module handles the generation of unique member IDs for the
Anantya Foundation volunteer system.

ID Format: AF-CITYCODE-XXX
    - AF: Anantya Foundation prefix
    - CITYCODE: 3-letter city code (e.g., DEL for Delhi)
    - XXX: Sequential number (001, 002, etc.)

Example: AF-DEL-001, AF-MUM-015

The module maintains persistent counters per city to ensure
uniqueness across application restarts.
"""

import json
from pathlib import Path

# Directory paths for data files
BASE_DIR = Path(__file__).resolve().parents[1]   # app/
DATA_DIR = BASE_DIR / "data"

CITY_ALIASES_PATH = DATA_DIR / "city_aliases.json"
CITY_COUNTERS_PATH = DATA_DIR / "city_counters.json"

# Load city code mappings (city name -> 3-letter code)
with CITY_ALIASES_PATH.open() as f:
    city_aliases_map = json.load(f)

# Load persistent counters per city code
with CITY_COUNTERS_PATH.open() as f:
    city_counter_map = json.load(f)


def save_counters():
    """
    Persist the current counter state to disk.

    Writes the city_counter_map to city_counters.json to ensure
    ID sequences are maintained across application restarts.
    """
    with CITY_COUNTERS_PATH.open("w") as f:
        json.dump(city_counter_map, f, indent=2)


def generate_unique_id(city: str):
    """
    Generate a unique Anantya Foundation member ID.

    Parses the city from the location string, looks up the city code,
    increments the counter for that city, and returns a formatted ID.

    Args:
        city: Location string in format "City, Locality" or just "City"
              Example: "Delhi, Connaught Place" or "Mumbai"

    Returns:
        str: Unique member ID in format "AF-CITYCODE-XXX"
             Example: "AF-DEL-001"

    Raises:
        ValueError: If city input is empty or not a string

    Note:
        If the city is not found in the aliases map, 'XXX' is used
        as the city code as a fallback.
    """
    if not city or not isinstance(city, str):
            raise ValueError("Invalid city input")

    city_name = city.split(",")[0].strip().lower()

    city_code = city_aliases_map.get(city_name, 'XXX')

    if city_code not in city_counter_map:
        city_counter_map[city_code] = 0

    city_counter_map[city_code] += 1
    new_id = f"AF-{city_code}-{city_counter_map[city_code]:03d}"

    save_counters()
    return new_id


