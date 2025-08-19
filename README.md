# Final Round AI - Resume Analyzer

This project is the foundational implementation of the "Final Round AI" application, specifically the AI Resume Analyzer feature. It's a full-stack web application with a React frontend and a Flask (Python) backend.

This version uses the `spaCy` Natural Language Processing (NLP) library to perform an intelligent analysis of resumes and job descriptions.

## Features

-   A web interface to paste a resume and a job description.
-   An AI-powered backend service that analyzes the two texts and returns a weighted match score.
-   The analysis identifies a predefined list of skills and categorizes them into "required" and "nice-to-have".
-   A detailed results display showing the overall score, and lists of matched and missing skills, broken down by importance.
-   An **AI Resume Builder** that takes structured user input (experience, education, etc.) and generates a professionally formatted, text-based resume.

## Tech Stack

-   **Frontend:** React (created with Create React App)
-   **Backend:** Python (Flask) with `spaCy` for NLP.

## Getting Started

To run this application on your local machine, you will need to have Node.js and Python installed.

### 1. Backend Setup

The backend is a Python Flask application located in the `backend` directory.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the dependencies:**
    The backend dependencies are listed in the `requirements.txt` file at the root of the project.
    ```bash
    pip install -r ../requirements.txt
    ```
4.  **Download the spaCy Language Model:**
    The application uses a `spaCy` model for English. You need to download it before running the server.
    ```bash
    python -m spacy download en_core_web_sm
    ```
5.  **Run the Flask server:**
    ```bash
    python app.py
    ```
    The backend server will start on `http://127.0.0.1:5000`.

### 2. Frontend Setup

The frontend is a React application located in the `frontend` directory.

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install the dependencies:**
    ```bash
    npm install
    ```
3.  **Run the React development server:**
    ```bash
    npm start
    ```
    The frontend development server will start, usually on `http://localhost:3000`, and should open automatically in your browser.

### How It Works

The React frontend will be running on `localhost:3000` and provides two main pages:
-   `/` (Resume Analyzer): Makes API calls to the `/analyze` endpoint. The backend uses `spaCy` to process the texts, extracts skills using a `Matcher`, and returns a structured JSON object with the analysis to the frontend.
-   `/builder` (Resume Builder): Contains a form to build a resume. It makes API calls to the `/generate-resume` endpoint to get a formatted text-based resume.

The backend is configured with `Flask-CORS` to allow cross-origin requests from the frontend during development.
