# Bulk Certificate Generator

A Python backend application that generates certificates in bulk for multiple recipients. It provides REST APIs to create generation jobs, generate certificates, track job progress, list certificate records, and download generated PDF files.

## Features

- Bulk certificate generation for multiple recipients
- Recipient name and email validation
- PDF certificate generation using ReportLab
- SQLite database for storing jobs and certificate records
- Job status and success/failure tracking
- Individual certificate download
- Error handling so one certificate failure does not stop the remaining certificates
- Automated API tests using Pytest

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ReportLab
- Pytest

## Requirements

- Python installed
- pip package manager

## Installation

Clone the repository and open the project directory.

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd bulk-certificate-generator
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the dependencies.

```powershell
pip install -r requirements.txt
```

## Run the Application

Start the API server.

```powershell
uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check whether the API is running |
| POST | `/api/jobs/` | Create a bulk generation job |
| POST | `/api/jobs/{job_id}/generate` | Generate certificates for a job |
| GET | `/api/jobs/{job_id}` | Retrieve job status and counts |
| GET | `/api/jobs/{job_id}/certificates` | List certificates belonging to a job |
| GET | `/api/jobs/certificates/{certificate_id}/download` | Download a generated PDF |

## How It Works

1. Submit a list of recipients through the API.
2. The application validates recipient details and stores the job and certificate records in SQLite.
3. Call the generation endpoint to generate the certificates.
4. The application records the result for each certificate and updates the job status.
5. Retrieve job details, list certificate records, or download successful certificates.

Certificate generation runs synchronously when the generation endpoint is called. Job creation and generation are separate API operations.

## Run Tests

Execute the automated tests from the project root:

```powershell
pytest -v
```

The tests cover API availability, bulk job creation, invalid inputs, certificate generation, job status, certificate listing, individual generation failures, PDF downloading, and missing jobs.

## Storage

The SQLite database is created locally by the application. Generated PDF files are stored in the `certificates/` directory.

The database and generated PDFs are local runtime data and should not be committed to GitHub.

## Project Purpose

This project demonstrates backend API development, relational database integration, input validation, PDF generation, error handling, and automated testing.
