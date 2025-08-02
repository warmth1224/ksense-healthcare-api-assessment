# healthcare_api_assessment.py

import requests
import time
import logging
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure professional logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://assessment.ksensetech.com/api"
HEADERS = {"x-api-key": API_KEY}

# --- Utilities ---
def safe_request(url: str, max_retries: int = 5, delay: float = 1.0) -> Dict:
    """
    Performs a GET request with retry logic on transient errors.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.json()
            if response.status_code in [429, 500, 503]:
                wait_time = delay * (2 ** attempt)
                logging.warning(f"Transient error {response.status_code}, retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"Request failed with status code {response.status_code}")
                break
        except Exception as e:
            logging.error(f"Exception during request: {e}")
            time.sleep(delay)
    return None

# --- Scoring Functions ---
def score_bp(bp: str) -> int:
    """Scores blood pressure based on medical thresholds."""
    try:
        systolic, diastolic = map(int, bp.split("/"))
    except Exception:
        logging.debug("Invalid blood pressure format")
        return 0
    if systolic >= 140 or diastolic >= 90:
        return 3
    if 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return 2
    if 120 <= systolic < 130 and diastolic < 80:
        return 1
    if systolic < 120 and diastolic < 80:
        return 0
    return 0

def score_temp(temp) -> int:
    """Scores body temperature."""
    try:
        temp = float(temp)
        if temp >= 101.0:
            return 2
        if 99.6 <= temp <= 100.9:
            return 1
        if temp <= 99.5:
            return 0
    except Exception:
        logging.debug("Invalid temperature value")
        return 0
    return 0

def score_age(age) -> int:
    """Scores age based on risk groups."""
    try:
        age = int(age)
        if age > 65:
            return 2
        if 40 <= age <= 65:
            return 1
        if age < 40:
            return 0
    except Exception:
        logging.debug("Invalid age value")
        return 0
    return 0

def has_invalid_data(p: dict) -> bool:
    """
    Returns True if the patient record has missing or non-numeric blood pressure,
    temperature, or age fields.
    """
    try:
        bp = p.get("blood_pressure", "")
        systolic, diastolic = map(int, bp.split("/"))
        if systolic <= 0 or diastolic <= 0:
            return True
    except Exception:
        return True
    try:
        temp = float(p["temperature"])
        if temp <= 0:
            return True
    except Exception:
        return True
    try:
        age = int(p["age"])
        if age <= 0:
            return True
    except Exception:
        return True
    return False

# --- Main Logic ---
def get_all_patients() -> List[Dict]:
    """
    Fetches all patient records across paginated results.
    """
    patients = []
    page = 1
    while True:
        logging.info(f"Fetching page {page}...")
        url = f"{BASE_URL}/patients?page={page}&limit=5"
        result = safe_request(url)
        if not result or "data" not in result:
            break
        patients.extend(result["data"])
        if not result.get("pagination", {}).get("hasNext"):
            break
        page += 1
    logging.info(f"Total patients fetched: {len(patients)}")
    return patients

def build_alert_lists(patients: List[Dict]) -> Dict[str, List[str]]:
    """
    Builds categorized alert lists based on patient data.
    """
    high_risk = []
    fever = []
    bad_data = []
    for p in patients:
        pid = p.get("patient_id")
        if not pid:
            continue
        if has_invalid_data(p):
            bad_data.append(pid)
            continue

        bp_score = score_bp(p["blood_pressure"])
        temp_score = score_temp(p["temperature"])
        age_score = score_age(p["age"])
        total_score = bp_score + temp_score + age_score

        if total_score >= 4:
            high_risk.append(pid)

        try:
            if float(p["temperature"]) >= 99.6:
                fever.append(pid)
        except Exception:
            pass

    logging.info(f"High risk: {len(high_risk)} | Fever: {len(fever)} | Data issues: {len(bad_data)}")
    return {
        "high_risk_patients": sorted(set(high_risk)),
        "fever_patients": sorted(set(fever)),
        "data_quality_issues": sorted(set(bad_data)),
    }

def submit_results(alerts: Dict[str, List[str]]):
    """
    Submits the compiled assessment results to the server.
    """
    url = f"{BASE_URL}/submit-assessment"
    response = requests.post(url, headers={
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }, json=alerts)
    logging.info(f"Submission status: {response.status_code}")
    return response.json()

# --- Entry Point ---
if __name__ == "__main__":
    logging.info("Starting assessment...")
    patients = get_all_patients()
    alert_lists = build_alert_lists(patients)
    result = submit_results(alert_lists)
    logging.info(f"Assessment Result: {result}")
