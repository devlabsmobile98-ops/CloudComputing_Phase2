# 🚗 Cloud-Based Scenario Extraction System (NGSIM)

## 📌 Overview

This project implements a **cloud-based pipeline** for extracting and processing driving scenarios from the **NGSIM (Next Generation Simulation) dataset**.

The system identifies traffic scenarios (e.g., car-following, lane changes, near-collisions) and segments them into **fixed 5-second windows (50 frames)** containing:

* One **ego vehicle**
* Relevant **surrounding vehicles**
* A **scenario label**

The system was developed in two phases:

* **Phase 1:** Modular monolithic system
* **Phase 2 (this repository):** Fully **microservices-based cloud architecture**

---

## 🎯 Objectives

* Ingest raw NGSIM trajectory data into the cloud
* Process and detect meaningful driving scenarios
* Segment data into **strictly valid 5-second windows**
* Ensure **frame consistency and data integrity**
* Demonstrate **cloud-native system design**

---

## 🏗️ System Architecture (Phase 2)

The system is decomposed into independent **Dockerized microservices**:

```
                ┌──────────────┐
                │   API Gateway│
                └──────┬───────┘
                       │
 ┌──────────────┬──────────────┬──────────────┬──────────────┐
 │Preprocessing │ Detection    │ Window       │ Validation   │
 │Service       │ Service      │ Service      │ Service      │
 └──────────────┴──────────────┴──────────────┴──────────────┘
                       │
                 Google Cloud Storage
```

### 🔹 Services

* **Preprocessing Service**

  * Cleans raw NGSIM data
  * Handles missing values and formatting

* **Detection Service**

  * Identifies scenario types:

    * Car-following
    * Lane change
    * Near-collision
    * Sudden braking

* **Window Service**

  * Extracts candidate 5-second windows

* **Validation Service (CRITICAL IMPROVEMENT)**

  * Ensures:

    * Exactly **50 sequential frames**
    * Ego vehicle continuity
    * Surrounding vehicle frame alignment
  * Rejects invalid windows

* **API Gateway**

  * Orchestrates the pipeline
  * Provides a single entry point

---

## ☁️ Cloud Deployment

The system is deployed on **Google Cloud Platform (GCP)**:

* **Google Cloud Storage (GCS)**

  * Stores raw, processed, and output data

* **Compute Engine VM**

  * Runs Docker containers

* **Docker Compose**

  * Manages all microservices

---

## ⚙️ How to Run

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

## 📊 Example Results

### ✔️ Validation Summary

* Total windows checked: **242**
* Passed validation: **231**
* Failed validation: **11**

### ✔️ Accepted Scenario Windows

* Near collision: **79**
* Lane change: **69**
* Car following: **50**
* Sudden braking: **25**

### ❌ Rejected Windows

* Total rejected: **177**
* Main reason:

  * `ego_non_sequential_or_incomplete`

---

## 🔍 Key Improvement from Phase 1 (VERY IMPORTANT)

### 🚨 Problem in Phase 1

Phase 1 incorrectly assumed:

* A 5-second window = 50 rows
* ❌ Did NOT verify if frames were sequential
* ❌ Did NOT ensure ego/surrounding vehicles aligned

This led to:

* Broken time sequences
* Inconsistent scenario data
* Incorrect model inputs

---

### ✅ Phase 2 Solution (TA Feedback Applied)

We implemented **strict validation logic**:

#### ✔️ Ego Vehicle Validation

* Must have **exactly 50 frames**
* Frames must be **strictly sequential**

#### ✔️ Surrounding Vehicle Validation

* Must match the **same frame sequence**
* Must not have missing frames

#### ✔️ Window Rejection System

Invalid windows are:

* **Rejected**
* Logged with explicit reasons
* Saved in `windows_rejected.csv`

---

### 📈 Impact

* Ensures **true temporal consistency**
* Improves **data quality**
* Makes dataset suitable for:

  * Machine learning
  * Autonomous driving simulations

---

## 📂 Output Files

| File                     | Description                   |
| ------------------------ | ----------------------------- |
| `cleaned_data.csv`       | Preprocessed dataset          |
| `windows_summary.csv`    | Accepted windows              |
| `windows_rejected.csv`   | Rejected windows with reasons |
| `validation_report.json` | Overall validation stats      |
| `validation_details.csv` | Per-window validation logs    |

---

## 🎥 Scenario Visualization

Each scenario is visualized using:

* Ego vehicle (**red**)
* Surrounding vehicles (**blue**)
* Frame-by-frame animation (50 frames)

### Example Scenarios:

* Car-following
* Lane change
* Near-collision
* Sudden braking

### Improvements over Phase 1:

* Consistent frame sequences
* Only validated windows visualized
* Cleaner, more accurate animations

---

## 🔄 Phase 1 vs Phase 2

| Feature            | Phase 1          | Phase 2       |
| ------------------ | ---------------- | ------------- |
| Architecture       | Monolithic       | Microservices |
| Deployment         | Single app       | Docker + GCP  |
| Validation         | Weak             | Strict        |
| Frame consistency  | ❌ Not guaranteed | ✅ Enforced    |
| Rejection handling | ❌ None           | ✅ Implemented |
| Scalability        | Limited          | High          |

---

## 🚀 Future Work (Bonus)

* Cloud Run / serverless pipeline
* Apache Beam / Dataflow integration
* Real-time streaming scenario detection
* Monitoring & logging dashboards

---

## 👥 Team Contribution

All team members contributed to:

* System design
* Microservices implementation
* Cloud deployment
* Scenario logic & validation

---

## 📌 Conclusion

This project demonstrates a **robust, cloud-native system** for extracting high-quality driving scenarios from real-world data.

The transition from Phase 1 to Phase 2 significantly improved:

* Data correctness
* System scalability
* Architectural design

---
