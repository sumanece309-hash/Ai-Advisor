import base64

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, Disposition, FileContent, FileName, FileType, Mail

from src.config import FROM_EMAIL, SENDGRID_API_KEY


def send_email_with_pdf(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename="Certification_Roadmap.pdf",
):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        return False, "SendGrid not configured (SENDGRID_API_KEY / FROM_EMAIL missing)."

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )

    encoded = base64.b64encode(pdf_bytes).decode()
    message.attachment = Attachment(
        FileContent(encoded),
        FileName(filename),
        FileType("application/pdf"),
        Disposition("attachment"),
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True, "Email sent."
    except Exception as e:
        return False, str(e)