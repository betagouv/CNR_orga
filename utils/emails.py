import httpx
from django.conf import settings


def send_email(to, params, template_id):
    headers = {"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "sender": {"name": "Conseil National de la Refondation", "email": settings.DEFAULT_FROM_EMAIL},
        "to": to,
        "params": params,
        "templateId": template_id,
    }

    response = httpx.post(settings.BREVO_SMTP_URL, headers=headers, json=payload)
    return response.status_code == 200
