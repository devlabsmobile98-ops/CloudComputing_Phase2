from pathlib import Path
import argparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.config import ENRICHED_PATH, EVENTS_PATH, OUTPUT_DIR, DEFAULT_MAX_PER_TYPE, DEFAULT_WINDOW_SIZE
from common.io_utils import load_csv, load_json, ensure_dir
from window_service.windowing import save_event_windows

app = FastAPI(title="window-service", version="2.0.0")


class WindowRequest(BaseModel):
    enriched_path: str | None = None
    events_path: str | None = None
    output_dir: str | None = None
    max_per_type: int = DEFAULT_MAX_PER_TYPE
    window_size: int = DEFAULT_WINDOW_SIZE


def run_windowing(enriched_path: str | Path | None = None,
                  events_path: str | Path | None = None,
                  output_dir: str | Path | None = None,
                  max_per_type: int = DEFAULT_MAX_PER_TYPE,
                  window_size: int = DEFAULT_WINDOW_SIZE):
    enriched_path = Path(enriched_path or ENRICHED_PATH)
    events_path = Path(events_path or EVENTS_PATH)
    output_dir = Path(output_dir or OUTPUT_DIR)
    ensure_dir(output_dir)

    if not enriched_path.exists():
        raise FileNotFoundError(f"Enriched input file not found: {enriched_path}")
    if not events_path.exists():
        raise FileNotFoundError(f"Detected events file not found: {events_path}")

    df = load_csv(enriched_path)
    events = load_json(events_path)
    summary_df, rejected_df = save_event_windows(
        df,
        events,
        output_dir=str(output_dir),
        max_per_type=max_per_type,
        window_size=window_size,
    )

    return {
        "status": "success",
        "service": "windowing",
        "enriched_path": str(enriched_path),
        "events_path": str(events_path),
        "output_dir": str(output_dir),
        "windows_created": int(len(summary_df)),
        "windows_rejected": int(len(rejected_df)),
        "summary_path": str(output_dir / "windows_summary.csv"),
        "rejected_path": str(output_dir / "windows_rejected.csv"),
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "windowing"}


@app.post("/run")
def run_endpoint(request: WindowRequest):
    try:
        return run_windowing(request.enriched_path, request.events_path, request.output_dir, request.max_per_type, request.window_size)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--enriched", default=str(ENRICHED_PATH))
    parser.add_argument("--events", default=str(EVENTS_PATH))
    parser.add_argument("--output", default=str(OUTPUT_DIR))
    parser.add_argument("--max-per-type", type=int, default=DEFAULT_MAX_PER_TYPE)
    parser.add_argument("--window-size", type=int, default=DEFAULT_WINDOW_SIZE)
    args = parser.parse_args()
    result = run_windowing(args.enriched, args.events, args.output, args.max_per_type, args.window_size)
    print(f"Output windows saved to: {result['output_dir']}")
    print(f"Summary path: {result['summary_path']}")
    print(f"Rejected windows path: {result['rejected_path']}")
    print(f"Windows created: {result['windows_created']}")
    print(f"Windows rejected: {result['windows_rejected']}")
