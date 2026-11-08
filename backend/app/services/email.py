
import time 

from app.core.config import settings

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

def send_email(to:str, subject: str, body: str) -> None:
  print(f"\n--- EMAIL (console mode, nothing was sent) ---\nTo: {to}\nSubject: {subject}\n\n{body}---\n")