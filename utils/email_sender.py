import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def send_otp_email(email: str, otp: str):
    """
    Sends an OTP email to the admin using Resend.
    """
    try:
        html_content = f"""
        <div style="font-family: sans-serif; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
            <h2>Admin Login Verification</h2>
            <p>Your One-Time Password (OTP) is:</p>
            <h1 style="color: #007bff; letter-spacing: 5px;">{otp}</h1>
            <p>This code expires in 5 minutes.</p>
        </div>
        """

        params = {
            "from": "onboarding@resend.dev", # Update if you have a verified domain
            "to": [email],
            "subject": "Your Login OTP",
            "html": html_content
        }

        email_resp = resend.Emails.send(params)
        return email_resp
    except Exception:
        return None