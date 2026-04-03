curl -X POST http://localhost:8000/run-all \
  -H "Content-Type: application/json" \
  -d '{"input_path":"/app/raw/us101_input.csv","max_per_type":100}'
