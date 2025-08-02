<<<<<<< HEAD
# Ksense Healthcare API Risk Scoring

This project is part of the Ksense Healthcare API Assessment.

## 🔍 Objective

Analyze patient data from the simulated API and implement a scoring algorithm that:
- Flags high-risk patients (total score ≥ 4)
- Detects fever patients (temperature ≥ 99.6°F)
- Identifies data quality issues

## 🚀 How to Run

1. Replace your API key in `api_risk_scoring.py`:
```python
API_KEY = "your_api_key_here"
=======
# Healthcare API Assessment

This project provides a professional solution for analyzing and submitting patient risk assessment data via the KSenseTech API.

---

## Features
- Retrieves paginated patient data from a secure healthcare API
- Calculates patient risk scores based on age, temperature, and blood pressure
- Generates categorized alerts:
  - High risk
  - Fever patients
  - Data quality issues
- Submits alerts back to the assessment API
- Includes unit tests and logging
- CLI interface for execution
- `.env` support for secure API keys

---

## Installation
```bash
pip install -r requirements.txt
```

---

## Usage

### Run without submission
```bash
python run_assessment_cli.py
```

### Run and submit results
```bash
python run_assessment_cli.py --submit
```

---

## File Structure
```
.
├── healthcare_api_assessment.py   # Core logic
├── run_assessment_cli.py          # CLI execution tool
├── test_scoring.py                # Unit tests
├── requirements.txt               # Dependency list
├── .env.example                   # Environment variable template
├── README.md                      # Documentation
```

---

## Environment Variables
Create a `.env` file at the root with:
```env
API_KEY=your_api_key_here
```
This keeps your credentials secure and out of version control.

---

## Tests
```bash
python test_scoring.py
```

---

## Requirements
- Python 3.8+
- requests
- python-dotenv

---

## Author
Built with care and precision by Code Copilot 🤖

---

## Status
✅ Project is complete and professionally packaged for production use.
>>>>>>> 29387c6 (second commit)
