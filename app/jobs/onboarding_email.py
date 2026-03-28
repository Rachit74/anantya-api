"""
Onboarding Email Job

- Sends a welcome email to newly registered members
- Called as a FastAPI background task after successful onboarding
"""

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME="rachithooda09@gmail.com",
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM="noreply@anantyafoundation.in",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)


async def send_onboarding_email(member_data: dict) -> None:
    """
    Send a welcome email to a newly onboarded member.

    Args:
        member_data: Dictionary containing member information with keys:
            - email: Member's email address
            - fullname: Member's full name
            - member_id: Generated member ID
            - department: List of departments member joined
    """
    fm = FastMail(conf)

    departments = ", ".join(member_data.get("department", []))

    body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

            <h2 style="color: #6b21a8;">Welcome to Anantya Foundation!</h2>

            <p>Dear <strong>{member_data.get('fullname', 'Member')}</strong>,</p>

            <p>
            Thank you for joining Anantya Foundation as a volunteer. We're excited to have you on board!
            </p>

            <div style="background: #f9f9f9; padding: 16px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #6b21a8;">Your Member Details</h3>
                <p style="margin: 8px 0;"><strong>Member ID:</strong> <span style="font-family: monospace;">{member_data.get('member_id', '').upper()}</span></p>
                <p style="margin: 8px 0;"><strong>Departments:</strong> {departments}</p>
                <p style="margin: 8px 0;"><strong>Email:</strong> {member_data.get('email', '')}</p>
            </div>

            <p>
            Please keep your Member ID safe — you'll need it for future communications and to access member services.
            </p>

            <h3 style="color: #6b21a8;">What's Next?</h3>
            <ul>
                <li>Our team will review your application and verify your details.</li>
                <li>You'll be contacted about upcoming events and opportunities in your departments.</li>
                <li>Feel free to reach out if you have any questions.</li>
            </ul>

            <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 24px 0;" />

            <p style="font-size: 13px; color: #666;">
            If you did not register with Anantya Foundation, please disregard this email or contact us immediately.
            </p>

            <p style="color: #888; font-size: 12px;">
            — Anantya Foundation Team<br>
            <a href="https://anantyafoundation.in" style="color: #6b21a8;">anantyafoundation.in</a>
            </p>

        </body>
        </html>
        """

    message = MessageSchema(
        subject="Welcome to Anantya Foundation!",
        recipients=[member_data["email"]],
        body=body,
        subtype=MessageType.html,
    )

    await fm.send_message(message)
    print("Onboarding Mail sent!")