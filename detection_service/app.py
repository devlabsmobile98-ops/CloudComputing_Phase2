from pathlib import Path
import argparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.config import CLEANED_PATH, ENRICHED_PATH, EVENTS_PATH, PROCESSED_DIR
from common.io_utils import load_csv, save_json, ensure_dir
from detection_service.neighbors import find_leader_vehicle
from detection_service.metrics import add_safety_metrics
from detection_service.scenarios import add_scenario_flags, extract_events

app = FastAPI(title="detection-service", version="1.0.0")


class DetectionRequest(BaseModel):
    input_path: str | None = None
    enriched_path: str | None = None
    events_path: str | None = None


def run_detection(input_path: str | Path | None = None,
                  enriched_path: str | Path | None = None,
                  events_path: str | Path | None = None):
    input_path = Path(input_path or CLEANED_PATH)
    enriched_path = Path(enriched_path or ENRICHED_PATH)
    events_path = Path(events_path or EVENTS_PATH)
    ensure_dir(PROCESSED_DIR)

    if not input_path.exists():
        raise FileNotFoundError(f"Cleaned input file not found: {input_path}")

    df = load_csv(input_path)
    df = find_leader_vehicle(df)
    df = add_safety_metrics(df)
    df = add_scenario_flags(df)
    df.to_csv(enriched_path, index=False)

    events = extract_events(df)
    flat_events = []
    for _, items in events.items():
        flat_events.extend(items)

    save_json(flat_events, events_path)

    return {
        "status": "success",
        "service": "detection",
        "input_path": str(input_path),
        "enriched_path": str(enriched_path),
        "events_path": str(events_path),
        "rows": int(len(df)),
        "total_events": int(len(flat_events)),
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "detection"}


@app.post("/run")
def run_endpoint(request: DetectionRequest):
    try:
        return run_detection(request.input_path, request.enriched_path, request.events_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(CLEANED_PATH))
    parser.add_argument("--enriched", default=str(ENRICHED_PATH))
    parser.add_argument("--events", default=str(EVENTS_PATH))
    args = parser.parse_args()
    result = run_detection(args.input, args.enriched, args.events)
    print(f"Enriched data saved to: {result['enriched_path']}")
    print(f"Detected events saved to: {result['events_path']}")
    print(f"Total events: {result['total_events']}")
