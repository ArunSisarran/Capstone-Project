"""Sending email.

With EMAIL_BACKEND=console (the default) the message is printed in the server log, so development
never sends real mail. With EMAIL_BACKEND=smtp it goes out through any SMTP server (Gmail with an
app password, Brevo, ...): only the settings in .env change, never this code.
"""
import logging
import smtplib
import ssl
import time
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("app.email")

SMTP_TIMEOUT_SECONDS = 15
RESET_COOLDOWN_SECONDS = 60

_last_reset_email: dict[str, float] = {}

def allow_reset_email(address: str, now: float | None = None) -> bool:
    """False if this address was sent a reset email less than a minute ago."""
    now = time.monotonic() if now is None else now
    key = address.lower()
    if len(_last_reset_email) > 10_000:                      
        for old in [a for a, t in _last_reset_email.items() if now - t > RESET_COOLDOWN_SECONDS]:
            del _last_reset_email[old]
    last = _last_reset_email.get(key)
    if last is not None and now - last < RESET_COOLDOWN_SECONDS:
        return False
    _last_reset_email[key] = now
    return True

def reset_email_body(link: str) -> str:
  minutes = settings.password_reset_expire_minutes
  return (
    "Hi, \n\n"
    "Someone asked to reset the password for your Recipe Recommender account"
    f"Open this link to choose a new one (it works once and expires in {minutes})"
    f"{link}\n\n"
    "If you did not ask for this, ignore this email. Your password has not changed.\n"
  )

def send_email(to: str, subject: str, body: str) -> None:
    """Send one plain-text email. Never raises: a mail problem must not break the request.
    (The body holds the reset link, so it is never written to the log in smtp mode.)"""
    message = EmailMessage()
    message["To"] = to
    message["From"] = settings.mail_from or "no-reply@localhost"
    message["Subject"] = subject
    message.set_content(body)
    try:
        if settings.email_backend == "smtp":
            _send_with_smtp(message)
        else:
            print(f"\n--- EMAIL (console mode, nothing was sent) ---\nTo: {to}\nSubject: {subject}\n\n{body}---\n")
    except Exception:
        logger.exception("Could not send an email to %s", to)


def _send_with_smtp(message: EmailMessage) -> None:
    if not (settings.smtp_username and settings.smtp_password and settings.mail_from):
        raise RuntimeError("SMTP_USERNAME, SMTP_PASSWORD and MAIL_FROM must be set when EMAIL_BACKEND=smtp")
    context = ssl.create_default_context()
    if settings.smtp_port == 465:                             # encrypted from the first byte
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=SMTP_TIMEOUT_SECONDS,
                              context=context) as server:
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    else:                                                     # 587: start plain, then upgrade with STARTTLS
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=SMTP_TIMEOUT_SECONDS) as server:
            server.starttls(context=context)
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)