"""Sending email"""
from app.core.config import settings

def reset_email_body(link: str) -> str:
  minutes = settings.password_reset_expire_minutes
  return (
    "Hi, \n\n"
    "Someone asked to reset the password for your Recipe Recommender account"
    f"Open this link to choose a new one (it works once and expires in {minutes})"
    f"{link}\n\n"
    "If you did not ask for this, ignore this email. Your password has not changed.\n"
  )

def send_email(to:str, subject: str, body: str) -> None:
  print(f"\n--- EMAIL (console mode, nothing was sent) ---\nTo: {to}\nSubject: {subject}\n\n{body}---\n")