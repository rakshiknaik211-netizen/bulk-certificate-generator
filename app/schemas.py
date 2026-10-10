
from pydantic import BaseModel, EmailStr, Field, field_validator


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Recipient name cannot be empty")

        return value


class JobCreate(BaseModel):
    recipients: list[RecipientInput] = Field(min_length=1)


class JobResponse(BaseModel):
    job_id: int
    total_recipients: int
    status: str
    message: str