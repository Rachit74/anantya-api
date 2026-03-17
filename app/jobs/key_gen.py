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
import asyncpg

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


async def get_admin_mails(pool) -> list[dict]:
    """
    Fetch all admin records (email + fullname) from the members table.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT email, fullname FROM members WHERE is_admin = TRUE;")
        return [dict(row) for row in rows]


def gen_key() -> str:
    """
    Generate a cryptographically secure random signup key.
    """
    return secrets.token_hex(8)


async def update_db_key(pool, new_key: str) -> None:
    """
    Overwrite the ADMIN_SIGNUP_KEY value in the keys table.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE keys SET key_value = $1 WHERE key_name = 'ADMIN_SIGNUP_KEY';",
            new_key
        )


async def send_mail(admins: list[dict], new_key: str) -> None:
    """
    Send the new admin signup key to every admin via email.
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


async def rotate_admin_signup_key(pool) -> None:
    """
    Full rotation pipeline. Called as a FastAPI background task
    immediately after a successful admin signup.

    Steps:
        1. Pull all admin emails from the DB
        2. Generate a new signup key
        3. Write the new key to the DB
        4. Email every admin the new key
    """
    admins = await get_admin_mails(pool)

    if not admins:
        return

    new_key = gen_key()
    await update_db_key(pool, new_key)
    await send_mail(admins, new_key)