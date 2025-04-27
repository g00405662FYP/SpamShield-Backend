# SpamShield - Backend Flask API

This repository contains the backend server for SpamShield.
The backend provides RESTful API endpoints for email classification, user authentication, feedback collection, and history tracking.

---

## Project Structure

| File/Folder | Purpose |
|:---|:---|
| `app.py` | Main Flask app with API route definitions |
| `requirements.txt` | Backend dependencies (Flask, Supabase, scikit-learn, etc.) |
| `Dockerfile` | Configuration to containerize the backend for Google Cloud Run deployment |
| `spam_classifier.pkl` | Trained Naive Bayes spam detection model |
| `vectorizer.pkl` | TfidfVectorizer used for email text preprocessing |
| `tests/` | Folder for backend unit tests |
| `.env` | Environment variables for Supabase URL, API key, and JWT secret (excluded from GitHub) |

---

## Features

- **User Authentication**:
  - Secure signup and login using Supabase Auth.
  - JWT-based authorization for protected routes.

- **Spam Detection**:
  - Classify email content as "Spam" or "Ham" with confidence scores.
  - Upload raw email text or file contents.

- **Feedback Collection**:
  - Users can submit feedback (correct/incorrect classification) linked to each message.
  - Feedback is stored in Supabase for potential future model improvements.

- **History Tracking**:
  - Retrieve user's past classifications and feedback through authenticated API requests.

- **Cloud Deployment**:
  - Backend is containerized using Docker.
  - Deployed on Google Cloud Run for serverless scalability.

---

## Running Locally

1. Clone the repository:

```bash
git clone https://github.com/YOUR_ORG/SpamShield-Backend.git
cd SpamShield-Backend
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the Flask App
```bash
python myproject/app.py
```

## Key API Endpoints

| Method | Route       | Description                                   |
|:------:|:------------|:----------------------------------------------|
| POST   | `/signup`    | Register a new user                          |
| POST   | `/login`     | Authenticate and receive JWT token           |
| POST   | `/classify`  | Classify email content (JWT required)         |
| POST   | `/feedback`  | Submit feedback for a classification (JWT required) |
| GET    | `/history`   | Retrieve user's classification history (JWT required) |


## Security

- JWT Authentication: Protects endpoints requiring user sessions.
- CORS Configured: Frontend whitelisted for secure cross-origin requests.
- Environment Variables: Sensitive keys managed outside source control.
