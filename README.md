# Final Round AI - Resume Analyzer

This project is the foundational implementation of the "Final Round AI" application, specifically the AI Resume Analyzer feature. It's a full-stack web application with a React frontend and a Flask (Python) backend.

## Features

-   A web interface to paste a resume and a job description.
-   A backend service that analyzes the two texts and returns a match score based on keyword comparison.
-   A results display showing the score and the list of matching keywords.

## Tech Stack

-   **Frontend:** React (created with Create React App)
-   **Backend:** Python (Flask)

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
4.  **Run the Flask server:**
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

The React frontend will be running on `localhost:3000` and will make API calls to the Flask backend, which is running on `http://127.0.0.1:5000`. The backend is configured with `Flask-CORS` to allow cross-origin requests from the frontend during development.
