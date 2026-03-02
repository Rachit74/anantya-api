from pydantic import EmailStr

import resend

from dotenv import load_dotenv
import os

load_dotenv()


resend.api_key = os.getenv('RESEND_API_KEY')


def send_mail(email: EmailStr, member_af_id: str):
    try:
        r = resend.Emails.send({
            "from": "Anantya <onboarding@resend.dev>",
            "to": [email],
            "subject": "Anantya Foundation onboarding email",
            "html": f"""
                <p>Successful onboarding!</p>
                <p>Your Unique ID is <strong>{member_af_id}</strong></p>
            """
        })
        print("Mail Sent!", r)
    except Exception as e:
        print("Email failed:", str(e))