import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.from_email = settings.FROM_EMAIL
        self.api_key = settings.SENDGRID_API_KEY

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        if not self.api_key:
            logger.info(f"[EMAIL MOCK] To: {to}, Subject: {subject}")
            return True
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
            sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to),
                subject=subject,
                html_content=Content("text/html", body),
            )
            sg.client.mail.send.post(request_body=message.get())
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def send_incident_confirmation(self, to: str, incident_title: str, incident_id: str) -> bool:
        subject = f"SafeNZ – Incident Reported: {incident_title}"
        body = f"""
        <h2>Your incident has been reported</h2>
        <p>Incident: <strong>{incident_title}</strong></p>
        <p>Reference ID: <strong>{incident_id}</strong></p>
        <p>Our team will review your report shortly.</p>
        <p>Stay safe,<br>SafeNZ Team</p>
        """
        return await self.send_email(to, subject, body)

    async def send_password_reset(self, to: str, reset_token: str) -> bool:
        subject = "SafeNZ – Password Reset"
        body = f"""
        <h2>Password Reset</h2>
        <p>Use the following token to reset your password:</p>
        <p><strong>{reset_token}</strong></p>
        <p>This token expires in 1 hour.</p>
        """
        return await self.send_email(to, subject, body)

    async def send_alert_notification(self, to: str, alert_title: str, message: str) -> bool:
        subject = f"EMERGENCY ALERT: {alert_title}"
        body = f"""
        <div style="background:#ff4444;color:white;padding:20px;">
        <h2>⚠️ Emergency Alert</h2>
        <h3>{alert_title}</h3>
        <p>{message}</p>
        <p>Stay safe and follow official guidance.</p>
        </div>
        """
        return await self.send_email(to, subject, body)


class SMSService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_FROM_NUMBER

    async def send_sms(self, to: str, message: str) -> bool:
        if not self.account_sid:
            logger.info(f"[SMS MOCK] To: {to}, Message: {message}")
            return True
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            client.messages.create(body=message, from_=self.from_number, to=to)
            return True
        except Exception as e:
            logger.error(f"SMS send failed: {e}")
            return False

    async def send_emergency_alert(self, to: str, region: str, message: str) -> bool:
        sms = f"SAFENZ ALERT – {region}: {message} Follow emergency guidance immediately."
        return await self.send_sms(to, sms)


email_service = EmailService()
sms_service = SMSService()
