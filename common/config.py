from pathlib import Path
import os

BASE_DIR = Path(os.getenv("BASE_DIR", Path(__file__).resolve().parents[1]))
RAW_DIR = Path(os.getenv("RAW_DIR", BASE_DIR / "raw"))
PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", BASE_DIR / "processed"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "output"))
RAW_INPUT_PATH = Path(os.getenv("RAW_INPUT_PATH", RAW_DIR / "us101_input.csv"))
CLEANED_PATH = Path(os.getenv("CLEANED_PATH", PROCESSED_DIR / "cleaned_data.csv"))
ENRICHED_PATH = Path(os.getenv("ENRICHED_PATH", PROCESSED_DIR / "enriched_data.csv"))
EVENTS_PATH = Path(os.getenv("EVENTS_PATH", PROCESSED_DIR / "detected_events.json"))
VALIDATION_REPORT_PATH = Path(os.getenv("VALIDATION_REPORT_PATH", PROCESSED_DIR / "validation_report.json"))
VALIDATION_DETAILS_PATH = Path(os.getenv("VALIDATION_DETAILS_PATH", PROCESSED_DIR / "validation_details.csv"))
WINDOWS_SUMMARY_PATH = Path(os.getenv("WINDOWS_SUMMARY_PATH", OUTPUT_DIR / "windows_summary.csv"))
REJECTED_WINDOWS_PATH = Path(os.getenv("REJECTED_WINDOWS_PATH", OUTPUT_DIR / "windows_rejected.csv"))
DEFAULT_MAX_PER_TYPE = int(os.getenv("DEFAULT_MAX_PER_TYPE", "100"))
DEFAULT_WINDOW_SIZE = int(os.getenv("DEFAULT_WINDOW_SIZE", "50"))
DEFAULT_HALF_WINDOW = DEFAULT_WINDOW_SIZE // 2
