"""
Unique ID Generator Service

This module handles the generation of unique member IDs for the
Anantya Foundation volunteer system.

ID Format: AF-CITYCODE-XXX
Example: AF-DEL-001, AF-MUM-015

City counters are stored in Firestore to persist across deployments.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

# load environment variables
load_dotenv()

# ----------------------------
# Firebase / Firestore Setup
# ----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
CREDS_PATH = BASE_DIR / "af-firebase-key.json"

FIREBASE_CREDS = os.getenv("FIREBASE_CREDS")

if FIREBASE_CREDS:
    # Production: credentials from env variable
    cred_dict = json.loads(FIREBASE_CREDS)
    cred = credentials.Certificate(cred_dict)
else:
    # Local development: credentials from file
    cred = credentials.Certificate(str(CREDS_PATH))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

COUNTERS_COLLECTION = "city_counters"

# ----------------------------
# Local Data Files
# ----------------------------

DATA_DIR = BASE_DIR / "app/data"
CITY_ALIASES_PATH = DATA_DIR / "city_aliases.json"

with CITY_ALIASES_PATH.open() as f:
    city_aliases_map = json.load(f)

# ----------------------------
# ID Generator
# ----------------------------

def generate_unique_id(city: str):
    """
    Generate a unique Anantya Foundation member ID.

    Args:
        city: Location string like "Delhi, Connaught Place"

    Returns:
        str: Unique member ID in format "AF-CITYCODE-XXX"
    """

    if not city or not isinstance(city, str):
        raise ValueError("Invalid city input")

    city_name = city.split(",")[0].strip().lower()
    city_code = city_aliases_map.get(city_name, "XXX")

    doc_ref = db.collection(COUNTERS_COLLECTION).document(city_code)

    @firestore.transactional
    def increment_counter(transaction, doc_ref):
        snapshot = doc_ref.get(transaction=transaction)

        if snapshot.exists:
            counter = snapshot.get("counter") + 1
        else:
            counter = 1

        transaction.set(doc_ref, {"counter": counter}, merge=True)

        return counter

    transaction = db.transaction()
    counter = increment_counter(transaction, doc_ref)

    new_id = f"AF-{city_code}-{counter:03d}"

    return new_id