# Neura-X - AI-Powered Patient-Centric Healthcare Intelligence Platform

Modern, intelligent patient portal and healthcare dashboard with AI-driven medical report analysis, anomaly detection, secure doctor-patient communication, and appointment management.

**Current Focus**: Patient-facing dashboard with real-time critical alerts from lab anomalies.

## Table of Contents

- [Overview](#overview)
- [Current Status & Core Features](#current-status--core-features)
- [Key Frontend Components](#key-frontend-components)
- [Backend Integration Points](#backend-integration-points)
- [API Endpoints (Patient Side)](#api-endpoints-patient-side)
- [Database Tables (Relevant)](#database-tables-relevant)
- [Technology Stack](#technology-stack)
- [Installation & Running](#installation--running)
- [Known Issues & Next Steps](#known-issues--next-steps)
- [Security Notes](#security-notes)
- [License](#license)

## Overview

**Neura-X** is an AI-powered healthcare intelligence platform primarily focused (at this stage) on the **patient portal**. It allows patients to:

- View their medical reports and AI-generated analyses
- See critical lab value alerts / anomalies with specialist recommendations
- Book & manage appointments
- Chat with doctors
- Interact with an AI health assistant (context-aware chatbot)
- Update personal profile (including medical history & allergies)

The system emphasizes **visual modern UI** (glassmorphism, gradients, animations) and real-time health insights.

## Current Status & Core Features

### Implemented & Working (Patient View)

- Modern animated patient dashboard with Tailwind CSS
- Profile picture + personal info section
- Statistics cards: Total Reports / Reviewed Reports / Critical Alerts / Upcoming Appointments
- Medical reports table with status badges (new/reviewed/critical/follow-up)
- Clickable Critical Alerts card showing abnormal lab values + recommended specialists
- Report list with view & PDF export links
- Appointment booking modal (doctor selection, date/time, reason)
- Doctor-patient messaging system (with polling)
- AI Health Assistant chatbot with context questions
- Profile update modal (picture, name, DOB, allergies, medications…)

### Partially Implemented / In Progress

- Real-time anomaly detection & critical alert popup
- Specialist recommendation logic based on abnormal values
- Full integration between report upload → anomaly detection → patient dashboard

## Key Frontend Components

| Component                        | Description                                          | Status     |
|:---------------------------------|------------------------------------------------------|------------|
| Patient Dashboard                | Main view with stats, reports table, analysis preview| ✅ Active  |
| Critical Alerts Card             | Shows count of critical anomalies                    | ⚠️ Needs API |
| Anomalies Details Panel          | Expandable view of abnormal values                   | Partial    |
| Anomaly Alert Modal (popup)      | Full-screen warning with specialist suggestions      | ⚠️ Needs API |
| Appointments Modal & Booking     | List + new booking form                              | ✅         |
| Doctor Chat Modal                | Select doctor → real-time chat (polling)             | ✅         |
| AI Assistant Modal               | Context questions → health Q&A (GROQ / Clinical BERT)| ✅         |
| Profile Modal                    | Update name, picture, medical history, allergies     | ✅         |

## Backend Integration Points (most important currently)

These endpoints are actively called from the patient dashboard JavaScript:

| Method | Endpoint                                 | Purpose                              | Current Status |
|--------|------------------------------------------|--------------------------------------|----------------|
| GET    | `/api/patient/<id>/reports`              | Load patient's medical reports       | Working?       |
| GET    | `/api/patient/<id>`                      | Load basic patient info              | Working?       |
| GET    | `/api/user/profile`                      | Load & update profile data           | Working        |
| GET    | `/api/doctors`                           | List doctors (for booking & chat)    | Working        |
| POST   | `/api/appointments`                      | Book new appointment                 | Working        |
| GET    | `/api/appointments`                      | List patient's appointments          | Working        |
| GET    | `/api/messages/with-doctor/<doctor_id>`  | Load chat history                    | Working        |
| POST   | `/api/messages/to-doctor/<doctor_id>`    | Send message to doctor               | Working        |
| **GET** | **`/api/patient/<id>/anomalies`**        | **Critical lab anomalies + specialists** | **404 – Missing** ← Highest priority fix |
| POST   | `/api/patient/chatbot`                   | AI assistant conversation            | Implemented?   |

**Critical missing endpoint right now**:

```text
GET /api/patient/<patient_id>/anomalies


Technology Stack
Frontend

HTML + Tailwind CSS (via CDN)
Vanilla JavaScript (ES6+, fetch, Chart.js)
Heroicons SVG icons

Backend

Flask (Python)
SQLite3
GROQ LLM API
Clinical BERT (via transformers?)
File handling: Pillow, PyMuPDF (fitz), PaddleOCR / Tesseract

Installation & Running

# 1. Activate virtual environment
source venv/bin/activate    # or venv\Scripts\activate on Windows

# 2. Install core dependencies (add more as needed)
pip install flask python-dotenv pillow PyMuPDF

# 3. (Optional – AI features)
pip install groq transformers torch

# 4. (Optional – OCR)
pip install paddleocr   # or pytesseract

# 5. Start the server
python app.py

License
MIT License
Built with ❤️ for better healthcare visibility


