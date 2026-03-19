"""
generates a time limited password reset token
updates that into the database, in the password_reset_tokens table
emails the link to the user
"""

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
import os
import secrets
from datetime import datetime, timedelta

load_dotenv()

MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

conf = ConnectionConfig(
    MAIL_USERNAME="rachithooda09@gmail.com",
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM="rachithooda09@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

def generate_token() -> str:
    token = secrets.token_urlsafe(16)
    return token

async def send_mail(email: str, token: str) -> None:
    fm = FastMail(conf)

    reset_link = f"https://anantyafoundation.vercel.app/reset-password?token={token}"

    body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; padding: 20px;">
                <h2>Password Reset Request</h2>
                <p>Hi,</p>
                <p>We received a request to reset the password for your account associated with <strong>{email}</strong>.</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}"
                       style="background-color: #4CAF50; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
                <p>This link will expire in <strong>30 minutes</strong>.</p>
                <p>If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.</p>
                <br>
                <p>Thanks,<br>The YourApp Team</p>
            </body>
        </html>
        """
        
    message = MessageSchema(
            subject="[Anantya Foundation] Reset Your Password",
            recipients=[email],
            body=body,
            subtype=MessageType.html,
        )

    await fm.send_message(message)


async def update_token(pool, member_data) -> None:
    token = generate_token()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO password_reset_tokens VALUES ($1, $2, $3, $4);",
            member_data['uuid'],
            token,
            datetime.now(),
            datetime.now() + timedelta(minutes=30)
        )

    await send_mail(member_data['email'], token=token)
