"""Scratch file: send ONE test email using the settings in .env.
Run from backend/:   python try_email.py            (sends to MAIL_FROM, i.e. to yourself)
                     python try_email.py me@gmail.com
Do not commit it."""
import sys
from email.message import EmailMessage

from app.core.config import settings
from app.services.email import _send_with_smtp

to = sys.argv[1] if len(sys.argv) > 1 else settings.mail_from
print(f"Sending a test email from {settings.mail_from!r} to {to!r} via {settings.smtp_host}:{settings.smtp_port} ...")

message = EmailMessage()
message["To"] = to
message["From"] = settings.mail_from
message["Subject"] = "Test from the Recipe backend"
message.set_content("If you can read this, SMTP works.")

try:
    _send_with_smtp(message)
except Exception as error:
    print(f"FAILED: {type(error).__name__}: {error}")
else:
    print("Sent! Check the inbox (and the spam folder).")