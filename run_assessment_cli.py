# run_assessment_cli.py

import argparse
import logging
from healthcare_api_assessment import get_all_patients, build_alert_lists, submit_results

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Healthcare Assessment CLI Tool")
    parser.add_argument("--submit", action="store_true", help="Submit the results to the server")
    args = parser.parse_args()

    logging.info("Starting CLI execution...")
    patients = get_all_patients()
    alerts = build_alert_lists(patients)

    logging.info("Generated Alert Lists:")
    for k, v in alerts.items():
        logging.info(f"{k}: {v}")

    if args.submit:
        logging.info("Submitting results...")
        result = submit_results(alerts)
        logging.info(f"Submission response: {result}")
    else:
        logging.info("Submission skipped. Use --submit to send data.")

if __name__ == "__main__":
    main()
