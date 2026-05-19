# 🧠 Synthesis.AI - Synthetic Healthcare Dataset Generation Platform
![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![GAN](https://img.shields.io/badge/GAN-Synthetic%20Data-red?style=for-the-badge)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

A **production-style multimodal healthcare dataset generation platform** that simulates realistic patient records using **GAN-based synthetic data modeling** and explains dataset characteristics using a **transformer-powered AI insight engine**.

Designed for:

* ML experimentation
* Healthcare analytics prototyping
* Privacy-safe research pipelines

---

#🖼️ Product Preview 
<img width="1883" height="906" alt="Screenshot 2026-05-19 233215" src="https://github.com/user-attachments/assets/eb15ba00-c4cd-4bb6-8674-790d55fb967a" />
<img width="1650" height="695" alt="image" src="https://github.com/user-attachments/assets/74ad5191-5eea-41a1-b13f-f0c0cfe51417" />
<img width="1070" height="894" alt="image" src="https://github.com/user-attachments/assets/de5a5ac6-d4c3-4346-a49c-1ed319f604cc" />
<img width="1353" height="821" alt="image" src="https://github.com/user-attachments/assets/2de7f21b-ed52-4fc5-b35b-86d10d32d393" />


# 🚀 Features

## 1️⃣ Synthetic Healthcare Dataset Generation

Generates realistic patient-level structured healthcare datasets including:

* Age
* BMI
* Random Blood Sugar (RBS)
* HbA1c
* Hypertension status
* Heart rate
* Respiratory rate
* SpO₂
* Time-series glucose signals

Powered by a **GAN-based synthetic data engine** that simulates realistic distributions.

---

## 2️⃣ Longitudinal Patient Time-Series Simulation

Simulates timestamped glucose readings:

```
Patient → Time-series RBS signals → Trend visualization
```

Useful for:

* Predictive modeling
* Anomaly detection
* Temporal ML experiments
* Sequence learning research

---

## 3️⃣ Transformer-Based Dataset Insight Engine

Includes an **Explainable AI analytics layer powered by FLAN-T5**

Before visualization, the transformer:

* analyzes dataset statistics
* interprets glucose distributions
* evaluates BMI risk variation
* explains dataset realism
* summarizes ML-readiness

Pipeline:

```
Dataset statistics
        ↓
Transformer inference
        ↓
Natural-language explanation
```

This converts the system into an:

> Explainable Synthetic Healthcare Data Platform

---

# 🤖 AI Insight Layer

Transformer-powered dataset explanation service:

```
POST /api/healthcare-gan/explain-stats
```

Automatically generates:

* dataset trend summaries
* glucose distribution comparisons
* metabolic risk indicators
* dataset realism insights
* ML training suitability feedback

Example response:

```json
{
  "status": "success",
  "explanation": "The dataset shows strong separation between diabetic and non-diabetic glucose levels..."
}
```

---

# 📊 Interactive Visualization Dashboard

Frontend built using:

* React
* TailwindCSS
* Recharts

Supports:

* tabular dataset preview
* patient-level inspection
* time-series visualization
* dataset summary insights
* AI-generated explanations

---

# 🏗️ System Architecture

Production-style microservices pipeline:

```
React Dashboard
        ↓
Flask API Gateway
        ↓
FastAPI ML Service
        ↓
GAN Generator + Insight Engine
```

### Benefits

* modular backend services
* scalable inference architecture
* separation of responsibilities
* agentic-AI extensibility support

---

# 🛠️ Tech Stack

| Layer                 | Technology                         |
| --------------------- | ---------------------------------- |
| Frontend              | React + TailwindCSS                |
| Visualization         | Recharts                           |
| Gateway API           | Flask                              |
| ML Service            | FastAPI                            |
| Synthetic Data Engine | GAN                                |
| Insight Engine        | HuggingFace Transformers (FLAN-T5) |
| Containerization      | Docker                             |
| Deployment            | Render-compatible microservices    |

---

# 📁 Project Structure

```
server/
 ├── app/
 │    └── routes/
 │         └── healthcare_gan_routes.py
 │
 ├── ml_service/
 │    ├── generate.py
 │    ├── gan_trainer.py
 │    ├── insight_engine.py
 │    └── main.py
 │
frontend/
 └── React dashboard
```

---

# 🔧 Example Workflow

```
Generate dataset
        ↓
Compute statistics
        ↓
Transformer insight engine
        ↓
Visualization dashboard
```

Produces:

* synthetic dataset
* statistical summary
* AI-generated explanation

---

# 🧪 API Endpoints

## Generate Synthetic Dataset

```
POST /api/healthcare-gan/generate
```

---

## Train GAN Model

```
POST /api/healthcare-gan/train
```

---

## Dataset Insight Engine

```
POST /api/healthcare-gan/explain-stats
```

Returns AI-generated dataset interpretation.

---

# 🔐 Why Synthetic Healthcare Data?

Supports:

* ML experimentation without PHI exposure
* healthcare analytics prototyping
* research simulations
* educational datasets

No real patient data required.

---

# 🚀 Future Enhancements

Planned agentic-AI upgrades:

* LangChain dataset quality agent
* training recommendation engine
* anomaly detection layer
* dataset realism scoring agent
* Kubernetes deployment support

---
