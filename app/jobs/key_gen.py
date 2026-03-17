"""
Admin Key Rotation Job

- Fetches all admin emails from the database
- Generates a new admin signup key
- Updates the .env file with the new key
- Mails the new key to all admin users
"""

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv, set_key
import os
import secrets
import asyncpg

load_dotenv()

ENV_FILE_PATH = ".env"
ADMIN_SINGUP_KEY = "ADMIN_SIGNUP_KEY"

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


async def get_admin_mails() -> list[dict]:
    """
    Fetch all admin records (email + fullname) from the admins table.

    Returns:
        List of dicts with 'email' and 'fullname' keys.
    """
    db_url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(db_url)

    try:
        rows = await conn.fetch("SELECT email, fullname FROM members WHERE is_admin=TRUE;")
        return [dict(row) for row in rows]
    finally:
        await conn.close()


def gen_key() -> str:
    """
    Generate a cryptographically secure random signup key.

    Returns:
        A 32-character hex string.
    """
    return secrets.token_hex(8)


def update_env_key(new_key: str) -> None:
    """
    Overwrite the ADMIN_SIGNUP_KEY value in the .env file.

    Args:
        new_key: The newly generated signup key.
    """
    set_key(ENV_FILE_PATH, ADMIN_SINGUP_KEY, new_key)
    # Also update the running process environment so the new key
    # is immediately effective without a restart.
    os.environ[ADMIN_SINGUP_KEY] = new_key


async def send_mail(admins: list[dict], new_key: str) -> None:
    """
    Send the new admin signup key to every admin via email.

    Args:
        admins: List of dicts with 'email' and 'fullname'.
        new_key: The newly generated signup key.
    """
    fm = FastMail(conf)

    for admin in admins:
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Anantya Foundation — New Admin Signup Key</h2>
            <p>Hello <strong>{admin['fullname']}</strong>,</p>
            <p>
              The previous admin signup key has been used and a new one has been
              generated automatically. Please use the key below for the next
              admin registration:
            </p>
            <p style="
              background: #f4f4f4;
              padding: 12px 16px;
              border-left: 4px solid #6b21a8;
              font-family: monospace;
              font-size: 15px;
              letter-spacing: 1px;
            ">
              {new_key}
            </p>
            <p style="color: #888; font-size: 12px;">
              Keep this key confidential. It will be replaced the moment it is used.
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


async def rotate_admin_signup_key() -> None:
    """
    Full rotation pipeline. Call this as a FastAPI background task
    immediately after a successful admin signup.

    Steps:
        1. Pull all admin emails from the DB
        2. Generate a new signup key
        3. Write the key to .env
        4. Email every admin the new key
    """
    admins = await get_admin_mails()

    if not admins:
        # Nothing to notify — skip rotation to avoid orphaned keys
        return

    new_key = gen_key()
    update_env_key(new_key)
    await send_mail(admins, new_key)