# Bulk Certificate Generator

A web-based bulk certificate generation application built with **FastAPI and Python**. It allows users to upload recipient details through a CSV file or enter them manually, generate personalized PDF certificates in bulk, track generation results, and download individual certificates or a ZIP archive.

## Features

- **Bulk recipient input:** Upload a CSV file containing recipient names and email addresses or enter recipient details manually.
- **Input validation:** Validates recipient names and email addresses and rejects invalid requests.
- **PDF certificate generation:** Generates personalized certificates using ReportLab.
- **Job management:** Creates a separate job for each bulk generation request.
- **Status tracking:** Tracks total recipients, successful generations, failed generations, and job status.
- **Individual downloads:** Download each successfully generated certificate as a PDF.
- **Bulk download:** Download all successfully generated certificates for a job in a ZIP archive.
- **Error handling:** Records individual certificate failures without stopping the remaining generation process.
- **Responsive frontend:** Provides a simple interface for submitting recipient details and viewing generation results.
- **Automated testing:** Includes Pytest tests for API functionality, validation, generation, failure handling, and downloads.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| SQLAlchemy | Database operations and ORM |
| SQLite | Persistent storage for jobs and certificate records |
| Pydantic | Request validation |
| ReportLab | PDF certificate generation |
| HTML and CSS | Frontend structure and styling |
| JavaScript | Frontend interactions and API communication |
| Pytest | Automated testing |

## Project Structure

- `main.py` initializes the FastAPI application and serves the frontend.
- `routes.py` implements the API endpoints for jobs, certificate generation, status tracking, and downloads.
- `models.py` defines the database models for jobs and certificates.
- `schemas.py` validates incoming recipient data.
- `database.py` configures the SQLite database and SQLAlchemy sessions.
- `certificate_generator.py` creates personalized PDF certificates using ReportLab.
- `frontend/` contains the user interface.
- `tests/` contains automated API tests.

## Prerequisites

- Python 3.10 or later recommended
- pip package manager

## Installation and Setup

### 1. Clone or download the repository

If cloning from GitHub, run:

```bash
git clone <your-repository-url>
cd bulk-certificate-generator
```

Replace `<your-repository-url>` with the actual repository URL. Alternatively, download and extract the project ZIP, then open the project folder in your terminal.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the appropriate activation method for your environment or run the commands from Command Prompt.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Running the Application

From the project root, start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Once the server starts, open the application in your browser.

- **Frontend:** http://127.0.0.1:8000/
- **Interactive API documentation:** http://127.0.0.1:8000/docs

Keep the terminal running while using the application. Press `Ctrl + C` to stop the server.

## How to Use the Application

1. Open the frontend in your browser.
2. Upload a CSV file with `name` and `email` columns, or enter recipient details manually in `name, email` format, one recipient per line.
3. Submit the recipient list to create a bulk generation job.
4. The application validates the input and creates a job and its associated certificate records.
5. The generation process creates a personalized PDF for each recipient.
6. Review the total, successful, and failed certificate counts.
7. Download individual certificates or download the successful certificates together as a ZIP file.

## API Endpoints

The backend exposes the following REST API endpoints.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/jobs/` | Create a bulk certificate generation job |
| `POST` | `/api/jobs/{job_id}/generate` | Generate certificates for a job |
| `GET` | `/api/jobs/{job_id}` | Retrieve job status and generation counts |
| `GET` | `/api/jobs/{job_id}/certificates` | List certificate records for a job |
| `GET` | `/api/jobs/certificates/{certificate_id}/download` | Download an individual PDF certificate |
| `GET` | `/api/jobs/{job_id}/download-zip` | Download successful certificates as a ZIP archive |


### Job Statuses

- `pending` — The job has been created but generation has not started.
- `processing` — Certificate generation is in progress.
- `completed` — All certificates were generated successfully.
- `completed_with_errors` — Generation finished, but one or more certificates failed.

## Processing Design

The application uses **synchronous certificate generation triggered by a separate API request**.

Job creation and certificate generation are separate operations. After a job is created, the client calls the generation endpoint to process its recipients. The application handles each certificate individually and records its result in the database.

This approach was selected to keep the implementation straightforward and suitable for demonstrating bulk-processing logic. It also ensures that a failure while generating one certificate does not prevent the application from attempting the remaining certificates.

For substantially larger workloads or production environments requiring non-blocking requests, a background task or task queue could be considered.

## Database and File Storage

The application uses SQLite to store job details and individual certificate records.

- **Database file:** `certificates.db`
- **Generated PDF directory:** `certificates/`

Job records store generation totals, status, and success/failure counts. Certificate records store recipient details, individual status, generated file paths, and failure information when applicable.

The database and generated PDF files are local runtime data. They should not be committed to the repository.

## Running Automated Tests

Run the following command from the project root:

```bash
pytest -v
```

The test suite checks:

- Root endpoint behavior
- Bulk job creation
- Empty recipient list rejection
- Invalid email rejection
- Successful certificate generation
- Job status retrieval
- Certificate listing
- Handling of an individual certificate generation failure
- PDF certificate download
- Nonexistent job handling

The tests use an isolated in-memory SQLite database and mock PDF generation where appropriate, so test runs do not need to create real certificates for every test.

## Design Decisions

- **FastAPI:** Provides API routing, request validation integration, and interactive API documentation.
- **SQLite and SQLAlchemy:** Provide relational storage and database operations without requiring a separate database server.
- **ReportLab:** Generates personalized PDF certificates programmatically.
- **Separate job and generation operations:** Allows the client to create a job before explicitly triggering generation.
- **Per-certificate error handling:** Allows processing to continue even when an individual certificate fails.
- **Frontend and REST API:** Provide both a user interface and API endpoints for interacting with the backend.

## Future Enhancements

- Background processing for large workloads
- Configurable certificate templates
- Authentication and role-based access
- Custom certificate fields and branding
- More detailed processing logs and retry support
