import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

PREPROCESSING_URL = os.getenv("PREPROCESSING_URL", "http://preprocessing-service:8001")
DETECTION_URL = os.getenv("DETECTION_URL", "http://detection-service:8002")
WINDOW_URL = os.getenv("WINDOW_URL", "http://window-service:8003")
VALIDATION_URL = os.getenv("VALIDATION_URL", "http://validation-service:8004")

app = FastAPI(title="api-gateway", version="2.0.0")


class PipelineRequest(BaseModel):
    input_path: str | None = None
    max_per_type: int = 100
    window_size: int = 50


def post_json(url: str, payload: dict):
    try:
        response = requests.post(url, json=payload, timeout=600)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Service unavailable: {url} | {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'api-gateway',
        'preprocessing_url': PREPROCESSING_URL,
        'detection_url': DETECTION_URL,
        'window_url': WINDOW_URL,
        'validation_url': VALIDATION_URL,
    }


@app.post('/preprocess')
def preprocess(request: PipelineRequest):
    return post_json(f"{PREPROCESSING_URL}/run", {"input_path": request.input_path})


@app.post('/detect')
def detect():
    return post_json(f"{DETECTION_URL}/run", {})


@app.post('/window')
def window(request: PipelineRequest):
    return post_json(f"{WINDOW_URL}/run", {"max_per_type": request.max_per_type, "window_size": request.window_size})


@app.post('/validate')
def validate():
    return post_json(f"{VALIDATION_URL}/run", {})


@app.post('/run-all')
def run_all(request: PipelineRequest):
    preprocess_result = post_json(f"{PREPROCESSING_URL}/run", {"input_path": request.input_path})
    detect_result = post_json(f"{DETECTION_URL}/run", {})
    window_result = post_json(f"{WINDOW_URL}/run", {"max_per_type": request.max_per_type, "window_size": request.window_size})
    validation_result = post_json(f"{VALIDATION_URL}/run", {})
    return {
        'status': 'success',
        'pipeline': [preprocess_result, detect_result, window_result, validation_result],
    }
