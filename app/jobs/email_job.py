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


async def send_mail(member: dict):

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background-color:#f4f6f9; font-family: Arial, sans-serif;">
      
      <table align="center" width="100%" cellpadding="0" cellspacing="0" 
             style="max-width:600px; margin:40px auto; background:#ffffff; 
             border-radius:8px; overflow:hidden; box-shadow:0 4px 10px rgba(0,0,0,0.08);">

        <tr>
          <td style="background:#2a5298; padding:30px; text-align:center; color:#ffffff;">
            <h1 style="margin:0;">Welcome to Anantya Foundation</h1>
          </td>
        </tr>

        <tr>
          <td style="padding:30px; color:#333333;">
            <p>Dear <strong>{member['fullname']}</strong>,</p>

            <p>
              We are pleased to confirm your onboarding as a volunteer.
              We look forward to your meaningful contribution.
            </p>

            <div style="margin:20px 0; padding:15px; background:#f0f4ff; 
                        border-left:4px solid #2a5298;">
              <strong>Your Unique Volunteer ID:</strong><br>
              <span style="font-size:18px; font-weight:bold;">
                {member['member_id']}
              </span>
            </div>

            <ul>
              <li>Maintain professionalism and punctuality.</li>
              <li>Follow your assigned team lead.</li>
              <li>Represent the foundation responsibly.</li>
              <li>Submit reports within deadlines.</li>
            </ul>

            <p>
              Regards,<br>
              <strong>Team Anantya Foundation</strong><br>
              📞 +91 8076339730<br>
              ✉ anantyafoundation03@gmail.com
            </p>
          </td>
        </tr>

      </table>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Welcome to Anantya Foundation",
        recipients=[member['email']],
        body=html_body,
        subtype="html"  # IMPORTANT
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    print("Mail Sent!")