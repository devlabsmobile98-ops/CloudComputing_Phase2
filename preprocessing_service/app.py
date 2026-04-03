from pathlib import Path
import argparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.config import RAW_INPUT_PATH, CLEANED_PATH, PROCESSED_DIR
from common.io_utils import save_csv, ensure_dir
from preprocessing_service.preprocess import load_and_clean_data

app = FastAPI(title="preprocessing-service", version="1.0.0")


class PreprocessRequest(BaseModel):
    input_path: str | None = None
    output_path: str | None = None


def run_preprocessing(input_path: str | Path | None = None, output_path: str | Path | None = None):
    input_path = Path(input_path or RAW_INPUT_PATH)
    output_path = Path(output_path or CLEANED_PATH)
    ensure_dir(PROCESSED_DIR)

    if not input_path.exists():
        raise FileNotFoundError(f"Raw input file not found: {input_path}")

    df = load_and_clean_data(str(input_path))
    save_csv(df, output_path)

    return {
        "status": "success",
        "service": "preprocessing",
        "input_path": str(input_path),
        "output_path": str(output_path),
        "rows": int(len(df)),
        "columns": list(df.columns),
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "preprocessing"}


@app.post("/run")
def run_endpoint(request: PreprocessRequest):
    try:
        return run_preprocessing(request.input_path, request.output_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(RAW_INPUT_PATH))
    parser.add_argument("--output", default=str(CLEANED_PATH))
    args = parser.parse_args()
    result = run_preprocessing(args.input, args.output)
    print(f"Cleaned data saved to: {result['output_path']}")
    print(f"Rows: {result['rows']}")
    print(f"Columns: {result['columns']}")
