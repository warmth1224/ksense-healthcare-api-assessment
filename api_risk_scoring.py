# /ksense/api_risk_scoring.py

import requests
import time
import re

BASE_URL = "https://assessment.ksensetech.com/api"
API_KEY = "YOUR_API_KEY_HERE"
HEADERS = {"x-api-key": API_KEY}

# Constants
MAX_PAGES = 20
PAGE_LIMIT = 5
RETRY_LIMIT = 3
RETRY_WAIT = 1

# Risk thresholds
TEMP_THRESHOLDS = {
    "normal": (None, 99.5),
    "low": (99.6, 100.9),
    "high": (101.0, None),
}

AGE_SCORES = [(65, 2), (40, 1), (0, 0)]

BP_CATEGORIES = [
    ((140, None), (90, None), 3),  # Stage 2
    ((130, 139), (80, 89), 2),     # Stage 1
    ((120, 129), (None, 79), 1),   # Elevated
    ((None, 119), (None, 79), 0),  # Normal
]

def retry_request(url):
    for attempt in range(RETRY_LIMIT):
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 429:
                time.sleep(RETRY_WAIT * (attempt + 1))
                continue
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException:
            time.sleep(RETRY_WAIT * (attempt + 1))
    return None

def parse_blood_pressure(bp):
    if not isinstance(bp, str) or "/" not in bp:
        return None
    try:
        sys_str, dia_str = bp.split("/")
        sys = int(re.sub(r"[^0-9]", "", sys_str))
        dia = int(re.sub(r"[^0-9]", "", dia_str))
        return (sys, dia)
    except:
        return None

def score_blood_pressure(bp_tuple):
    if not bp_tuple:
        return 0
    sys, dia = bp_tuple
    for sys_range, dia_range, score in BP_CATEGORIES:
        sys_ok = sys_range[0] is None or sys >= sys_range[0]
        if sys_range[1] is not None:
            sys_ok &= sys <= sys_range[1]
        dia_ok = dia_range[0] is None or dia >= dia_range[0]
        if dia_range[1] is not None:
            dia_ok &= dia <= dia_range[1]
        if sys_ok or dia_ok:
            return score
    return 0

def score_temperature(temp):
    try:
        temp = float(temp)
        if temp >= TEMP_THRESHOLDS["high"][0]:
            return 2
        elif TEMP_THRESHOLDS["low"][0] <= temp <= TEMP_THRESHOLDS["low"][1]:
            return 1
        elif temp <= TEMP_THRESHOLDS["normal"][1]:
            return 0
    except:
        pass
    return 0

def score_age(age):
    try:
        age = int(age)
        for min_age, score in AGE_SCORES:
            if age >= min_age:
                return score
    except:
        pass
    return 0

def is_invalid(value):
    return value is None or str(value).strip().lower() in ("", "null", "n/a", "invalid", "unknown")

def process_patients():
    patients = []
    page = 1
    while page <= MAX_PAGES:
        url = f"{BASE_URL}/api/patients?page={page}&limit={PAGE_LIMIT}"
        data = retry_request(url)
        if not data or "data" not in data or not data["data"]:
            break
        patients.extend(data["data"])
        page += 1
    return patients

def evaluate_patients(patients):
    high_risk = []
    fever = []
    issues = []

    for p in patients:
        pid = p.get("patient_id") or p.get("patient id")
        bp = parse_blood_pressure(p.get("blood_pressure") or p.get("blood_prcssure"))
        temp = p.get("temperature")
        age = p.get("age")

        bp_score = score_blood_pressure(bp)
        temp_score = score_temperature(temp)
        age_score = score_age(age)

        total_score = bp_score + temp_score + age_score

        if total_score >= 4:
            high_risk.append(pid)
        try:
            if float(temp) >= 99.6:
                fever.append(pid)
        except:
            pass

        if is_invalid(bp) or is_invalid(temp) or is_invalid(age):
            issues.append(pid)

    return {
        "high_risk_patients": high_risk,
        "fever_patients": fever,
        "data_quality_issues": issues
    }

def submit_results(results):
    url = f"{BASE_URL}/api/submit-assessment"
    try:
        res = requests.post(url, json=results, headers={**HEADERS, "Content-Type": "application/json"})
        return res.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    patients = process_patients()
    results = evaluate_patients(patients)
    print("Submission payload:", results)
    response = submit_results(results)
    print("API Response:", response)
