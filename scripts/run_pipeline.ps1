Invoke-RestMethod -Method Post -Uri "http://localhost:8000/run-all" -ContentType "application/json" -Body '{"input_path":"/app/raw/us101_input.csv","max_per_type":100}'
