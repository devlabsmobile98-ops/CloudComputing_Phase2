FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8003
CMD ["uvicorn", "window_service.app:app", "--host", "0.0.0.0", "--port", "8003"]
