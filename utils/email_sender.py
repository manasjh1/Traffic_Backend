import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP email to admin"""
    try:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 500px;">
            <h2 style="color: #333;">Traffic Management Login</h2>
            <p>Your login code:</p>
            <h1 style="background: #f4f4f4; padding: 20px; text-align: center; letter-spacing: 5px; font-family: monospace;">
                {otp}
            </h1>
            <p style="color: #666;">This code expires in 5 minutes.</p>
        </div>
        """

        response = resend.Emails.send({
            "from": "Traffic System <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your Login Code",
            "html": html_content
        })
        
        return True
        
    except Exception as e:
        print(f"Email failed: {e}")
        return False