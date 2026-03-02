from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

from dotenv import load_dotenv
import os

load_dotenv()


conf = ConnectionConfig(
    MAIL_USERNAME="rachithooda09@gmail.com",
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM="noreply@anantyafoundation.in",  # custom sender
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)


async def send_mail(email: EmailStr, member_af_id: str):
    message = MessageSchema(
        subject = "Welcome to anantya foundation",
        recipients=[email],
        body=
        f"""
            Successful onboarding to anatya foundation!\n
            Your Unique ID for anantya foundation is {member_af_id}.
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    print("Mail Sent!")