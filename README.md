# Cloud-Based Scenario Extraction System (NGSIM)

## Overview
In this project we built a cloud-based pipeline to extract and process driving scenarios from the NGSIM (Next Generation Simulation) dataset.

The main goal of the system is to detect different traffic situations (such as car-following, lane changes, near-collisions, and sudden braking) and break them into fixed 5-second windows (50 frames).
Each window contains:
- one ego vehicle
- relevant surrounding vehicles
- a scenario label

We developed the system in two phases:
- Phase 1: a modular monolithic system
- Phase 2 (this repository): a mircroservices-based cloud system using Docker

---

## Objectives
The main objectives of this project were:
- Read and process raw NGSIM trajectory data
- Detect meaningfull driving scenarios from the data
- Segment the data into strictly valid 5-second windows (50 frames)
- Ensure that all frames in each window are sequential (no gaps)
- Make sure surrounding vehicles align with the ego vehicles frames
- Design and implement the system using a cloud/mircoservices approach

---

System Architecture (Phase 2)

In Phase 2, we redesigned the system into separate Dockerized microservices so that each part of the pipeline runs independently. 
<img width="606" height="267" alt="image" src="https://github.com/user-attachments/assets/314b4730-8ad3-45af-bc96-79cc58841a05" />

Each service handles a specific part of the pipeline, and they work together to process the data step by step.

Services
Preprocessing Service
  - Cleans the raw NGSIM data
  - Handles missing values and formatting issues

Detection Service
Identifies scenario types:
    - Car-following
    - Lane change
    - Near-collision
    - Sudden braking

Window Service
  - Extracts candidate 5-second windows (50 frames) from detected events

Validation Service 
This was added to fix issues from Phase 1.
It ensures that:
    - Each window has exactly 50 sequential frames
    - The ego vehicle is continuous across all frames
    - Surrounding vehicle match the same frame sequence
    - Invalid windows are rejected 

API Gateway
  - Acts as the main entry point for the system
  - Runs the full pipeline by calling each service in order

Cloud Deployment
We designed the suystem so it can run on the cloud using Docker containers.
Our setup includes:
  - Google Cloud Storage (GCS)
    Used to stre raw, processed, and output data
  - Compute Engine VM
    Runs the Docker containers
  - Docker Compose
    Used to start and manage all microservices together

## How to Run
### 1. Start Services

```bash
docker compose up --build -d
```
### 2. Run Full Pipeline
```bash
curl -X POST http://localhost:8000/run-all \
  -H "Content-Type: application/json" \
  -d '{
    "input": "raw/us101_input.csv",
    "cleaned": "processed/cleaned_data.csv",
    "summary": "output/windows_summary.csv",
    "rejected": "output/windows_rejected.csv",
    "validation_report": "processed/validation_report.json",
    "validation_details": "processed/validation_details.csv"
  }'
```
### 3. Check Outputs
```bash
ls processed/
ls output/
```

---

## Example Results
### Validation Summary
- Total windows checked:242
- Passed validation:231
- Failed validation:11

### Accepted Scenario Windows
- Near collision:79
- Lane change:69
- Car following:50
- Sudden braking:25

### Rejected Windows
- Total rejected:177
- Main reason:
  `ego_non_sequential_or_incomplete`

---

## Key Improvement from Phase 1 
### What went wrong in Phase 1
In Phase 1, we assumed that:
  - A 5-second window = 50 rows
However, we didn't properly check
  - whether the frames were actually sequential 
  - whether the ego and surrpunding vehicles had matching frame indices  

Because of this, we ended up with:
  - broken or skipped frame sequences
  - inconsistent scenario windows
  - unreliable data for further analysis

### What we fixed in Phase 2 (based on TA feedback)
To addressed these issues, we added a strict validation step before saving any window.

#### Ego Vehicle Validation
  - Must have exactly 50 frames
  - Frames must be strictly sequential (no gaps)

#### Surrounding Vehicle Validation
  - Must follow the same frame sequence as the ego vehicle
  - Must not have missing or misaligned frames

#### Window Rejection System
  - Invalid windows are not saved
  - Each rejected windo includes a clear reason
  - All rejected cases are stored in:
    `windows_rejected.csv`

### Impact of these changes
These improvements made a big difference in  data quality:
  - Ensures true temporal consistency
  - Removes invalid or misleading data
  - produces cleaner and more reliable scenario windows

This makes the dataset more suitable for:
  - machine learning models
  - autonomous driving analysis


## Output Files

| File                     | Description                         |
| ------------------------ | -----------------------------       |
| `cleaned_data.csv`       | Preprocessed dataset                |
| `windows_summary.csv`    | Accepted scenario windows           |
| `windows_rejected.csv`   | Rejected windows with reasons       |
| `validation_report.json` | Overall validation sumary           |
| `validation_details.csv` | Detailed validation logs per window |

## Scenario Visualization
We visualize each scenario using:
  - Ego vehicle (red)
  - Surrounding vehicles (blue)
  - Frame-by-frame animation (50 frames)

### Example Scenarios:
  - Car-following
  - Lane change
  - Near-collision
  - Sudden braking

### Improvements over Phase 1:
  - Frames are now always sequential and consistent
  - Only validated windows are used
  - Visualizations are more accurate and stable

---

Phase 1 vs Phase 2

| Feature            | Phase 1          | Phase 2               |
| ------------------ | ---------------- | -------------         |
| Architecture       | Monolithic       | Microservices         |
| Deployment         | Single app       | Docker + cloud-ready  |
| Validation         | Weak             | Strict                |
| Frame consistency  | Not guaranteed   | Enforced              |
| Rejection handling | None             | Implemented           |
| Scalability        | Limited          | Improved              |

---

## Future Work 

Some improvements we could consider next:
  - Deploying services using Cloud Run / serverless
  - Using Dataflow or Apache Beam for scalability
  - Real-time scenario detection from streaming data
  - Adding monitoring and logging dashboards

---

## Team Contribution

All team members contributed to:
  - system design
  - microservices implementation
  - cloud setup
  - design a cleaner system architecture

---

## Conclusion

Overall, this project demonstrates how we improved a basic pipeline into a more reliable, cloud-ready system.

Moving from Phase 1 to Phase 2 helped us:
  - fix major data consistency issues
  - improve scalability
  - design a cleaner system architecture 

---
