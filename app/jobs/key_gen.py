"""
Admin Key Rotation Job

- Fetches all admin emails from the database
- Generates a new admin signup key
- Updates the key in the database
- Mails the new key to all admin users
"""

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv
import os
import secrets
import string
from app.models.schemas import AdminSignup

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


def gen_key(length: int = 16) -> str:
    """
    Generate a cryptographically secure alphanumeric signup key.
    Combines uppercase letters, lowercase letters, and digits.

    Returns:
        A random alphanumeric string of the given length.
    """
    charset = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(charset) for _ in range(length))


async def send_mail(admins: list[dict], new_key: str, new_admin_data: AdminSignup) -> None:
    """
    Send the new admin signup key to every admin via email.
    """
    fm = FastMail(conf)

    for admin in admins:
        body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

                <h2>Anantya Foundation — New Admin Signup Key</h2>

                <p>Hello <strong>{admin['fullname']}</strong>,</p>

                <p>
                The previous admin signup key has been consumed and a new one has been
                generated automatically. Please use the key below for the next admin registration:
                </p>

                <!-- New key — shown first -->
                <p style="
                background: #f4f4f4;
                padding: 12px 16px;
                border-left: 4px solid #6b21a8;
                font-family: monospace;
                font-size: 15px;
                letter-spacing: 1px;
                ">{new_key}</p>

                <!-- Who used the previous key -->
                <p style="font-size: 14px; color: #333;">
                <strong>Used by:</strong>
                <span style="font-family: monospace;">{new_admin_data.member_id.upper()}</span>
                — This member ID just completed admin registration using the previous key.
                </p>

                <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 20px 0;" />

                <p style="font-size: 13px; color: #555;">
                <strong>⚠ One-Time Use Only</strong> — This key will be permanently invalidated the moment it is used for the next admin registration.
                </p>
                <p style="font-size: 13px; color: #555;">
                <strong>🔒 Keep This Confidential</strong> — Do not share this key over public channels or unencrypted forwards. It grants full admin access to the platform.
                </p>
                <p style="font-size: 13px; color: #555;">
                <strong>✅ Automatic Rotation</strong> — Keys are rotated automatically after every use. You will always receive the latest key via this email.
                </p>

                <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 20px 0;" />

                <p style="color: #888; font-size: 12px;">
                If you believe this registration was unauthorised or suspicious, please contact your system administrator immediately and revoke the new admin's access.
                </p>

                <p>— Anantya Foundation System</p>

            </body>
            </html>
            """

        message = MessageSchema(
            subject="[Anantya Foundation] New Admin Signup Key Generated",
            recipients=[admin["email"]],
            body=body,
            subtype=MessageType.html,
        )

        await fm.send_message(message)


async def rotate_admin_signup_key(pool, new_admin_data: AdminSignup) -> None:
    """
    Full rotation pipeline. Called as a FastAPI background task
    immediately after a successful admin signup.

    Steps:
        1. Pull all admin emails from the DB
        2. Generate a new signup key
        3. Write the new key to the DB
        4. Release connection, then email every admin the new key
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT email, fullname FROM members WHERE is_admin = TRUE;")
        admins = [dict(row) for row in rows]

        if not admins:
            return

        new_key = gen_key()
        await conn.execute(
            "UPDATE keys SET key_value = $1 WHERE key_name = 'ADMIN_SIGNUP_KEY';",
            new_key
        )

    # Connection released before sending emails
    await send_mail(admins, new_key, new_admin_data=new_admin_data)