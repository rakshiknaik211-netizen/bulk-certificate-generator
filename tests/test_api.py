
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


# A separate in-memory database for tests
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Bulk Certificate Generator API is running"
    )


def test_create_bulk_job():
    response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {
                    "name": "Kumar X",
                    "email": "kumar@example.com"
                },
                {
                    "name": "Raha Sha",
                    "email": "rahasha@example.com"
                },
                {
                    "name": "Amy",
                    "email": "amy@example.com"
                }
            ]
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["total_recipients"] == 3
    assert data["status"] == "pending"
    assert data["job_id"] > 0


def test_reject_empty_recipient_list():
    response = client.post(
        "/api/jobs/",
        json={"recipients": []}
    )

    assert response.status_code == 422


def test_reject_invalid_email():
    response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {
                    "name": "Asha Kumar",
                    "email": "not-an-email"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_generate_certificates_for_bulk_job(tmp_path, monkeypatch):
    from app import routes

    def fake_generate_certificate(recipient_name, certificate_id):
        file_path = tmp_path / f"certificate_{certificate_id}.pdf"
        file_path.write_bytes(b"%PDF-1.4 test certificate")
        return str(file_path)

    monkeypatch.setattr(
        routes,
        "generate_certificate",
        fake_generate_certificate
    )

    # Create a job with two recipients
    create_response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {"name": "Asha Kumar", "email": "asha@example.com"},
                {"name": "Rahul Sharma", "email": "rahul@example.com"}
            ]
        }
    )

    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]

    # Generate their certificates
    generate_response = client.post(
        f"/api/jobs/{job_id}/generate"
    )

    assert generate_response.status_code == 200

    data = generate_response.json()
    assert data["status"] == "completed"
    assert data["total_recipients"] == 2
    assert data["successful_count"] == 2
    assert data["failed_count"] == 0


def test_get_job_status(tmp_path, monkeypatch):
    from app import routes

    def fake_generate_certificate(recipient_name, certificate_id):
        file_path = tmp_path / f"certificate_{certificate_id}.pdf"
        file_path.write_bytes(b"%PDF-1.4 test certificate")
        return str(file_path)

    monkeypatch.setattr(
        routes,
        "generate_certificate",
        fake_generate_certificate
    )

    create_response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {"name": "Asha Kumar", "email": "asha@example.com"}
            ]
        }
    )
    job_id = create_response.json()["job_id"]

    client.post(f"/api/jobs/{job_id}/generate")

    response = client.get(f"/api/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["successful_count"] == 1
    assert response.json()["failed_count"] == 0


def test_list_job_certificates():
    create_response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {"name": "Asha Kumar", "email": "asha@example.com"},
                {"name": "Rahul Sharma", "email": "rahul@example.com"}
            ]
        }
    )
    job_id = create_response.json()["job_id"]

    response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["certificates"]) == 2 


def test_one_certificate_failure_does_not_stop_others(
    tmp_path, monkeypatch
):
    from app import routes

    def fake_generate_certificate(recipient_name, certificate_id):
        if recipient_name == "Rahul Sharma":
            raise RuntimeError("Simulated PDF generation failure")

        file_path = tmp_path / f"certificate_{certificate_id}.pdf"
        file_path.write_bytes(b"%PDF-1.4 test certificate")
        return str(file_path)

    monkeypatch.setattr(
        routes,
        "generate_certificate",
        fake_generate_certificate
    )

    create_response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {"name": "Asha Kumar", "email": "asha@example.com"},
                {"name": "Rahul Sharma", "email": "rahul@example.com"},
                {"name": "Priya Rao", "email": "priya@example.com"}
            ]
        }
    )

    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]

    response = client.post(
        f"/api/jobs/{job_id}/generate"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total_recipients"] == 3
    assert data["successful_count"] == 2
    assert data["failed_count"] == 1
    assert data["status"] == "completed_with_errors"


def test_download_generated_certificate(tmp_path, monkeypatch):
    from app import routes

    def fake_generate_certificate(recipient_name, certificate_id):
        file_path = tmp_path / f"certificate_{certificate_id}.pdf"
        file_path.write_bytes(b"%PDF-1.4 test certificate")
        return str(file_path)

    monkeypatch.setattr(
        routes,
        "generate_certificate",
        fake_generate_certificate
    )

    create_response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {"name": "Asha Kumar", "email": "asha@example.com"}
            ]
        }
    )
    job_id = create_response.json()["job_id"]

    client.post(f"/api/jobs/{job_id}/generate")

    list_response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )
    certificate_id = list_response.json()["certificates"][0][
        "certificate_id"
    ]

    download_response = client.get(
        f"/api/jobs/certificates/{certificate_id}/download"
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
    assert download_response.content.startswith(b"%PDF")


def test_get_nonexistent_job():
    response = client.get("/api/jobs/99999")
    assert response.status_code == 404
