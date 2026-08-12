from typing import Dict, Any, List, Optional
import os


def _validate_attachment_path(filepath: str) -> str:
    """Restrict outbound attachments to the application's managed data folder."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_root = os.path.realpath(os.path.join(project_root, "data"))
    resolved_path = os.path.realpath(filepath)
    if os.path.commonpath([data_root, resolved_path]) != data_root:
        raise ValueError("Attachments must be located in the managed data directory.")
    if not os.path.isfile(resolved_path):
        raise FileNotFoundError("Attachment not found.")
    return resolved_path

# Note: email.prepare just formats and validates the email intent.
# email.send actually sends it and is marked with requires_approval=True in the registry.

def prepare_email(
    to: str, 
    subject: str, 
    body: str, 
    attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Prepare an email payload for human review."""
    
    if not to or not to.strip() or to.strip() == "None":
        raise ValueError("Cannot prepare email: The recipient's email address is missing. Please provide a valid email address.")
    
    valid_attachments = []
    if attachments:
        for att in attachments:
            valid_attachments.append(_validate_attachment_path(att))
                
    return {
        "status": "prepared",
        "to": to,
        "subject": subject,
        "body": body,
        "attachments": valid_attachments
    }

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(
    to: str, 
    subject: str, 
    body: str, 
    attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Actually send the email using SMTP."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_pass:
        raise ValueError("SMTP credentials are not configured in environment.")

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachments:
        for filepath in attachments:
            filepath = _validate_attachment_path(filepath)
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        text = msg.as_string()
        server.sendmail(smtp_user, to, text)
        server.quit()
        
        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "attachments_count": len(attachments) if attachments else 0,
            "message": "Email successfully sent."
        }
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {str(e)}")
