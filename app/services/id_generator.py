"""
Unique ID Generator Service

This module handles the generation of unique member IDs for the
Anantya Foundation volunteer system.

ID Format: AF-DDMMYY-XXX
Example: AF-240326-001, AF-240326-015

Date-based counters are stored in Firestore to persist across deployments.
"""

import json
import os
from datetime import datetime
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

COUNTERS_COLLECTION = "date_counters"

# ----------------------------
# ID Generator
# ----------------------------

def generate_unique_id():
    """
    Generate a unique Anantya Foundation member ID.

    Returns:
        str: Unique member ID in format "AF-DDMMYY-XXX"
              e.g. "AF-250326-001"
    """

    date_code = datetime.now().strftime("%d%m%y")   # e.g. "250326"

    doc_ref = db.collection(COUNTERS_COLLECTION).document(date_code)

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

    return f"AF-{date_code}-{counter:03d}"