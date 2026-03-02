import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]   # app/
DATA_DIR = BASE_DIR / "data"

CITY_ALIASES_PATH = DATA_DIR / "city_aliases.json"
CITY_COUNTERS_PATH = DATA_DIR / "city_counters.json"

with CITY_ALIASES_PATH.open() as f:
    city_aliases_map = json.load(f)

with CITY_COUNTERS_PATH.open() as f:
    city_counter_map = json.load(f)


def save_counters():
    with CITY_COUNTERS_PATH.open("w") as f:
        json.dump(city_counter_map, f, indent=2)

"""
gen_af_id -> generate anantya foundation id
will generate unique id specific to anantya foundation
will make sure no id dublication
"""
def gen_af_id(city: str):
    """
    city: str -> format is of type -> City, Localit or City
    we get city out of the proper input, eg:- Delhi
    then do Delhi.tolower() and get the alise of of that map
    generate an id like AF-DEL-001
    check if id list contains that id, if yes then increase the number by 1, so AF-DEL-002
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


