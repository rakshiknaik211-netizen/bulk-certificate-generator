
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


# Store generated PDFs in the project's certificates folder
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "certificates"


def generate_certificate(recipient_name: str, certificate_id: int) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create a unique PDF filename
    filename = f"certificate_{certificate_id}.pdf"
    file_path = OUTPUT_DIR / filename

    # Use a landscape A4 page
    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(str(file_path), pagesize=(page_width, page_height))

    # Draw the certificate design
    pdf.setStrokeColor(colors.HexColor("#24476B"))
    pdf.setLineWidth(4)
    pdf.rect(25, 25, page_width - 50, page_height - 50)

    pdf.setFillColor(colors.HexColor("#24476B"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 110,
        "CERTIFICATE OF ACHIEVEMENT"
    )

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 180,
        "This certificate is proudly presented to"
    )

    pdf.setFillColor(colors.HexColor("#24476B"))
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 230,
        recipient_name
    )

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 280,
        "In recognition of participation and achievement."
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        page_width / 2,
        65,
        f"Certificate ID: {certificate_id}"
    )

    pdf.save()

    return str(file_path)