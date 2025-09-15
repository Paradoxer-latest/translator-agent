import os
from contextlib import asynccontextmanager
from email.message import EmailMessage

import aiosmtplib
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("EMAIL")
SMTP_PASSWORD = os.getenv("PASSWORD")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "true").lower() in {"1", "true", "yes", "on"}


@asynccontextmanager
async def transporter():
    """
    Async context manager yielding a connected and authenticated SMTP client.
    Usage:
        async with transporter() as smtp:
            await smtp.send_message(message)
    """
    client = aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT, start_tls=SMTP_STARTTLS)
    await client.connect()
    if SMTP_USER and SMTP_PASSWORD:
        await client.login(SMTP_USER, SMTP_PASSWORD)
    try:
        yield client
    finally:
        try:
            await client.quit()
        except Exception:
            await client.close()


async def send_email(
    to_email: str,
    subject: str,
    text: str,
    html: str | None = None,
    from_email: str | None = None,
) -> None:
    """
    Convenience helper to send an email using the configured transporter.
    """
    msg = EmailMessage()
    msg["From"] = from_email or (SMTP_USER or "")
    msg["To"] = to_email
    msg["Subject"] = subject

    if html:
        msg.set_content(text or "")
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(text)

    async with transporter() as client:
        await client.send_message(msg)