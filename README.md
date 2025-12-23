## OpenSeeWe — AI-Powered Video Analysis Platform

This repository contains the working prototype of OpenSeeWe, an AI-powered video analysis platform that showcases Product Watcher AI — a system designed to analyze and understand video footage intelligently.

## Features
- Modern frontend built with React/Next.js
- FastAPI backend for AI model serving and data processing
- Seamless communication between frontend and backend
- Easy local setup for testing and development

## Installation & Setup
1. Clone the Repository <br>
```bash
git clone https://github.com/Riddhi-Sharma27/OpenSeeWe-SIH25197-Prototype-Website.git && \
cd OpenSeeWe-SIH25197-Prototype-Website
```
<br>
2. Setup the Backend (FastAPI)<br>

```bash
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
```

The backend will start at `http://localhost:8000/` by default.  
<br>
3. Setup the Frontend (Next.js)<br>
In a new terminal:
```bash
cd frontend && npm install && npm run prod
```

The frontend will start at `http://localhost:3000/`

## Usage
Once both servers are running:
- Open your browser at http://localhost:3000/ <br>
- Interact with the Product Watcher AI demo interface

The backend processes the requests and returns AI-driven video insights
