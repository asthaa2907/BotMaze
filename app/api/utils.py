import requests
from app.core.config import settings
import time
import requests
from app.core.config import settings

def send_whatsapp_message(to: str, message: str, access_token: str, phone_number_id: str):
    """
    Send a WhatsApp text message via the Meta Graph API.
    to: E.164 phone (e.g., '919876543210')
    access_token: long-lived system user token
    phone_number_id: the *Phone Number ID* from API Setup (NOT WABA ID)
    """
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"   # <-- URL must look like this

    headers = {
        "Authorization": f"Bearer {access_token.strip()}",                 # <-- single space after Bearer
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    # helpful diagnostics in your console, token masked
    print(f"→ WA send: to={to}, phone_number_id={phone_number_id}, token={access_token[:8]}…")

    r = requests.post(url, json=payload, headers=headers)
    print("WhatsApp API Response:", r.status_code, r.text)

    if r.status_code != 200:
        # bubble up a clear error to your caller
        raise RuntimeError(f"WhatsApp send failed ({r.status_code}): {r.text}")

    return r.json()


def normalize_phone(phone: str) -> str:
    """Normalize phone number by removing '+' and country code formatting"""
    if not phone:
        return ""
    phone = phone.strip().replace("+", "")
    if phone.startswith("91") and len(phone) == 12:
        return phone
    elif not phone.startswith("91"):
        return f"91{phone}"
    return phone
