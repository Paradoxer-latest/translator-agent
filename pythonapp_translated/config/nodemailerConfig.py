import os
from dotenv import load_dotenv
import aiosmtplib

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


class _Transporter:
    async def sendMail(self, *, from_email: str | None = None, to: str, subject: str, text: str):
        sender = from_email or EMAIL
        if not sender or not PASSWORD:
            raise RuntimeError("EMAIL or PASSWORD is not set in environment variables")

        message = f"From: {sender}\r\nTo: {to}\r\nSubject: {subject}\r\n\r\n{text}"

        smtp = aiosmtplib.SMTP(hostname="smtp.gmail.com", port=587, start_tls=True)
        await smtp.connect()
        try:
            await smtp.starttls()
            await smtp.login(sender, PASSWORD)
            await smtp.sendmail(sender, [to], message)
        finally:
            try:
                await smtp.quit()
            except Exception:
                pass


# Exported transporter-like instance (mapped from Nodemailer)
transporter = _Transporter()
