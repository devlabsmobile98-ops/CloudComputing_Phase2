from pathlib import Path
import argparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

from common.config import OUTPUT_DIR, VALIDATION_REPORT_PATH, VALIDATION_DETAILS_PATH
from common.io_utils import save_json, ensure_parent
from validation_service.validator import validate_window_file

app = FastAPI(title="validation-service", version="1.0.0")


class ValidationRequest(BaseModel):
    output_dir: str | None = None
    validation_report_path: str | None = None
    validation_details_path: str | None = None


def run_validation(output_dir: str | Path | None = None,
                   validation_report_path: str | Path | None = None,
                   validation_details_path: str | Path | None = None):
    output_dir = Path(output_dir or OUTPUT_DIR)
    validation_report_path = Path(validation_report_path or VALIDATION_REPORT_PATH)
    validation_details_path = Path(validation_details_path or VALIDATION_DETAILS_PATH)

    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    files = [p for p in output_dir.rglob('*.csv') if p.name not in {'windows_summary.csv', 'windows_rejected.csv'}]
    details = [validate_window_file(path) for path in sorted(files)]
    passed = sum(1 for d in details if d['status'] == 'passed')
    failed = len(details) - passed

    ensure_parent(validation_report_path)
    ensure_parent(validation_details_path)
    pd.DataFrame(details).to_csv(validation_details_path, index=False)
    report = {
        "status": "success",
        "service": "validation",
        "output_dir": str(output_dir),
        "window_files_checked": len(details),
        "windows_passed": passed,
        "windows_failed": failed,
        "details_path": str(validation_details_path),
    }
    save_json(report, validation_report_path)
    return report


@app.get('/health')
def health():
    return {"status": "ok", "service": "validation"}


@app.post('/run')
def run_endpoint(request: ValidationRequest):
    try:
        return run_validation(request.output_dir, request.validation_report_path, request.validation_details_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(OUTPUT_DIR))
    parser.add_argument('--report', default=str(VALIDATION_REPORT_PATH))
    parser.add_argument('--details', default=str(VALIDATION_DETAILS_PATH))
    args = parser.parse_args()
    result = run_validation(args.output, args.report, args.details)
    print(f"Validation details saved to: {result['details_path']}")
    print(f"Windows checked: {result['window_files_checked']}")
    print(f"Windows passed: {result['windows_passed']}")
    print(f"Windows failed: {result['windows_failed']}")
