
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import Job, Certificate
from .schemas import JobCreate, JobResponse
from .certificate_generator import generate_certificate

from pathlib import Path
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    request: JobCreate,
    db: Session = Depends(get_db)
):
    try:
        # Count the recipients in this request
        total = len(request.recipients)

        # Create one job record
        job = Job(
            total_recipients=total,
            successful_count=0,
            failed_count=0,
            status="pending"
        )

        db.add(job)
        db.flush()

        # Create one certificate record per recipient
        for recipient in request.recipients:
            certificate = Certificate(
                job_id=job.id,
                recipient_name=recipient.name,
                recipient_email=str(recipient.email),
                status="pending"
            )
            db.add(certificate)

        # Save the job and all recipient records
        db.commit()
        db.refresh(job)

        return JobResponse(
            job_id=job.id,
            total_recipients=job.total_recipients,
            status=job.status,
            message="Bulk generation job created successfully"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create generation job"
        )

@router.post("/{job_id}/generate")
def generate_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="This job has already been processed or started"
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .order_by(Certificate.id)
        .all()
    )

    job.status = "processing"
    db.commit()

    for certificate in certificates:
        try:
            file_path = generate_certificate(
                certificate.recipient_name,
                certificate.id
            )

            certificate.file_path = file_path
            certificate.status = "success"
            certificate.error_message = None

        except Exception:
            certificate.status = "failed"
            certificate.file_path = None
            certificate.error_message = (
                "Certificate generation failed"
            )

        # Save each recipient's result independently
        db.commit()

    # Recalculate counts from the database
    job = db.get(Job, job_id)

    job.successful_count = (
        db.query(Certificate)
        .filter(
            Certificate.job_id == job_id,
            Certificate.status == "success"
        )
        .count()
    )

    job.failed_count = (
        db.query(Certificate)
        .filter(
            Certificate.job_id == job_id,
            Certificate.status == "failed"
        )
        .count()
    )

    if job.failed_count == 0:
        job.status = "completed"
    else:
        job.status = "completed_with_errors"

    db.commit()

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful_count": job.successful_count,
        "failed_count": job.failed_count,
        "message": "Certificate generation finished"
    }

@router.get("/{job_id}")
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful_count": job.successful_count,
        "failed_count": job.failed_count,
        "message": "Job status retrieved successfully"
    }


@router.get("/{job_id}/certificates")
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .order_by(Certificate.id)
        .all()
    )

    return {
        "job_id": job.id,
        "total_recipients": job.total_recipients,
        "certificates": [
            {
                "certificate_id": cert.id,
                "recipient_name": cert.recipient_name,
                "recipient_email": cert.recipient_email,
                "status": cert.status,
                "error_message": cert.error_message
            }
            for cert in certificates
        ]
    }


@router.get("/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = db.get(Certificate, certificate_id)

    if certificate is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "success" or not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Generated certificate is not available"
        )

    file_path = Path(certificate.file_path)

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate PDF file not found"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf"
    )