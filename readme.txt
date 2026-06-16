# 📘 LLM Flask Processing Pipeline  
## Fault-Tolerant CSV Processing System with Failure Recovery

---

## 🚀 Overview

This project is a Flask-based backend system designed to process CSV data using an LLM API (Gemini or similar).

It ensures reliable processing even when external APIs fail by implementing:
- State persistence
- Retry mechanisms
- Checkpoint-based recovery
- Duplicate billing protection

The system is built to handle real-world failures like **504 Gateway Timeout**, rate limits, and network interruptions.

---

## ⚙️ Features

- 📄 CSV file upload and processing  
- 🤖 LLM-based row-wise processing  
- 🔁 Automatic retry with backoff strategy  
- 💾 Persistent state tracking (resume support)  
- 🔐 Request hashing (prevents duplicate API calls)  
- 🧪 JSON validation and auto-repair  
- ⚠️ Quarantine system for failed rows  
- 📊 Logging for monitoring and debugging  

---

## 🏗️ Project Structure
llm_flask_project/
│
├── app.py
├── llm_processor.py
├── refinement.py
├── json_repair.py
├── state_manager.py
│
├── data/
│ ├── inputs/
│ ├── outputs/
│ └── checkpoints/
│
├── logs/
├── failure_analysis.md
├── requirements.txt
└── README.md


---

## 🔄 Workflow

1. User uploads a CSV file via Flask API  
2. System generates a unique `tracking_id`  
3. Each row is sent to the LLM API  
4. Output is validated and stored  
5. State is updated after every successful row  
6. If interrupted, processing resumes from last checkpoint  

---

## ⚠️ Failure Handling Strategy

The system handles multiple failure scenarios:

- **504 Gateway Timeout**
- **Rate limiting / quota exhaustion**
- **Network failures**
- **Invalid or partial JSON responses**

### Recovery Mechanism:
- State is saved after every row  
- Processing resumes from last saved checkpoint  
- Failed rows are retried automatically  
- Unrecoverable rows go to quarantine folder  

---

## 🔐 Anti Double-Billing System

To prevent duplicate API charges:
- Each request is assigned a unique hash  
- Hash is stored after successful processing  
- Before API call, system checks if hash exists  
- If exists → API call is skipped  

This ensures **no duplicate billing even during retries**.

---

## 🧪 API Endpoints

### Upload CSV

POST /upload


### Process Data

POST /process/<tracking_id>


### Check Status

GET /status/<tracking_id>


---

## 🛠️ Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
2. Run the Flask server
python app.py
3. Open in browser
http://127.0.0.1:5000/
📊 System Highlights
Modular architecture
Fault-tolerant LLM pipeline
Safe restart after crashes
Cost-efficient API usage
Clean logging and debugging system
🧠 Tech Stack
Python
Flask
Pandas
Google Gemini / LLM API
JSON processing
File-based state management