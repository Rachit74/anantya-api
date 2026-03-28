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

    fullname = member_data.get('fullname', 'Member')
    member_id = member_data.get('member_id', '').upper()

    body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Welcome to Anantya Foundation</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&display=swap" rel="stylesheet"/>
</head>
<body style="margin:0;padding:0;background-color:#f5efe6;font-family:'DM Sans','Trebuchet MS',Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5efe6;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#fffdf8;border-radius:8px;overflow:hidden;box-shadow:0 4px 24px rgba(101,67,33,0.12);border:1px solid #e8d9c4;">

          <!-- Header -->
          <tr>
            <td style="background-color:#5c3a1e;padding:40px 48px 32px;text-align:center;">
              <div style="width:80px;height:80px;border-radius:50%;background-color:#f5efe6;border:3px solid #c8a97a;margin:0 auto 16px;display:flex;align-items:center;justify-content:center;overflow:hidden;">
                <table cellpadding="0" cellspacing="0" style="width:60px;height:60px;">
                  <tr>
                    <td align="center" style="font-size:28px;line-height:1;">🤝</td>
                  </tr>
                </table>
              </div>
              <p style="margin:0 0 6px;font-family:'DM Sans',Arial,sans-serif;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#c8a97a;">Est. with Purpose</p>
              <h1 style="margin:0;font-family:'DM Serif Display','Georgia',serif;font-size:30px;font-weight:normal;color:#fff8ee;letter-spacing:1px;">Anantya Foundation</h1>
              <p style="margin:6px 0 0;font-size:12px;color:#d4a96a;letter-spacing:1px;font-style:italic;">परिवर्तन अनंतते वर्तते</p>
              <div style="margin:18px auto 0;width:60px;height:2px;background:linear-gradient(to right,#e8923a,#f5c842,#6cbf6c,#5b9bd5,#9b59b6);border-radius:2px;"></div>
            </td>
          </tr>

          <!-- Colorful accent bar -->
          <tr>
            <td style="height:5px;background:linear-gradient(to right,#e8923a 20%,#f5c842 20% 40%,#6cbf6c 40% 60%,#5b9bd5 60% 80%,#9b59b6 80%);"></td>
          </tr>

          <!-- Welcome Banner -->
          <tr>
            <td style="background-color:#fdf4e7;padding:20px 48px;text-align:center;border-bottom:1px solid #e8d9c4;">
              <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:12px;letter-spacing:3px;text-transform:uppercase;color:#7a4a1e;font-weight:700;">✦ Welcome Aboard ✦</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 48px;">

              <p style="margin:0 0 20px;font-size:16px;line-height:1.7;color:#3a2010;">Dear <strong style="color:#5c3a1e;">{fullname}</strong>,</p>

              <p style="margin:0 0 24px;font-size:15px;line-height:1.8;color:#5a4030;">
                We are pleased to confirm your onboarding as a volunteer with Anantya Foundation. Your decision to contribute your time and effort toward community service is deeply valued, and we look forward to your active participation.
              </p>

              <!-- Volunteer ID Box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                <tr>
                  <td style="background-color:#fdf4e7;border:1px solid #d4a96a;border-left:5px solid #e8923a;border-radius:6px;padding:20px 24px;">
                    <p style="margin:0 0 6px;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#7a4a1e;">Your Unique Volunteer ID</p>
                    <p style="margin:0;font-size:26px;font-weight:bold;color:#5c3a1e;letter-spacing:2px;font-family:'Courier New',monospace;">{member_id}</p>
                    <p style="margin:8px 0 0;font-size:12px;color:#8a6a50;line-height:1.5;">Kindly use this ID in all communications, event registrations, attendance submissions, and reports.</p>
                  </td>
                </tr>
              </table>

              <!-- Guidelines -->
              <p style="margin:0 0 16px;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#7a4a1e;font-family:'DM Sans',Arial,sans-serif;font-weight:700;">As Part of Your Onboarding</p>

              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                <tr>
                  <td style="padding:12px 0;border-bottom:1px solid #f0e6d8;vertical-align:top;">
                    <table cellpadding="0" cellspacing="0"><tr>
                      <td style="width:28px;vertical-align:top;padding-top:2px;">
                        <div style="width:22px;height:22px;background-color:#e8923a;border-radius:50%;text-align:center;line-height:22px;font-size:11px;color:#ffffff;font-family:Arial,sans-serif;font-weight:bold;">1</div>
                      </td>
                      <td style="font-size:14px;line-height:1.7;color:#4a3020;padding-left:12px;">Maintain <strong style="color:#5c3a1e;">professionalism and punctuality</strong> during all activities.</td>
                    </tr></table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:12px 0;border-bottom:1px solid #f0e6d8;vertical-align:top;">
                    <table cellpadding="0" cellspacing="0"><tr>
                      <td style="width:28px;vertical-align:top;padding-top:2px;">
                        <div style="width:22px;height:22px;background-color:#f5c842;border-radius:50%;text-align:center;line-height:22px;font-size:11px;color:#5c3a1e;font-family:Arial,sans-serif;font-weight:bold;">2</div>
                      </td>
                      <td style="font-size:14px;line-height:1.7;color:#4a3020;padding-left:12px;">Follow the <strong style="color:#5c3a1e;">guidance of your assigned team lead</strong>.</td>
                    </tr></table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:12px 0;border-bottom:1px solid #f0e6d8;vertical-align:top;">
                    <table cellpadding="0" cellspacing="0"><tr>
                      <td style="width:28px;vertical-align:top;padding-top:2px;">
                        <div style="width:22px;height:22px;background-color:#6cbf6c;border-radius:50%;text-align:center;line-height:22px;font-size:11px;color:#ffffff;font-family:Arial,sans-serif;font-weight:bold;">3</div>
                      </td>
                      <td style="font-size:14px;line-height:1.7;color:#4a3020;padding-left:12px;">Represent the foundation <strong style="color:#5c3a1e;">responsibly in public and on social media</strong>.</td>
                    </tr></table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:12px 0;vertical-align:top;">
                    <table cellpadding="0" cellspacing="0"><tr>
                      <td style="width:28px;vertical-align:top;padding-top:2px;">
                        <div style="width:22px;height:22px;background-color:#5b9bd5;border-radius:50%;text-align:center;line-height:22px;font-size:11px;color:#ffffff;font-family:Arial,sans-serif;font-weight:bold;">4</div>
                      </td>
                      <td style="font-size:14px;line-height:1.7;color:#4a3020;padding-left:12px;">Submit <strong style="color:#5c3a1e;">event photos, videos, and reports</strong> within the given deadlines.</td>
                    </tr></table>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 24px;font-size:14px;line-height:1.8;color:#5a4030;">
                You will soon receive updates regarding upcoming events, project allocations, and reporting structure. Stay active on official communication channels to avoid missing important announcements.
              </p>

              <p style="margin:0 0 32px;font-size:14px;line-height:1.8;color:#5a4030;">
                For any queries, feel free to reach out to us. We look forward to your meaningful contribution.
              </p>

              <!-- Document Download Button -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:36px;">
                <tr>
                  <td style="background-color:#fdf4e7;border:1px dashed #d4a96a;border-radius:6px;padding:20px 24px;text-align:center;">
                    <p style="margin:0 0 8px;font-size:13px;color:#7a4a1e;font-weight:700;letter-spacing:1px;">📄 Volunteer Welcome Kit</p>
                    <p style="margin:0 0 14px;font-size:12px;color:#8a6a50;">Download your onboarding document, code of conduct &amp; event calendar.</p>
                    <a href="https://drive.google.com/uc?export=download&amp;id=1psyg5cZtv1WTKyqEV0BYF1xW6x23Z1Wu" style="display:inline-block;background-color:#5c3a1e;color:#fff8ee;text-decoration:none;font-size:13px;font-weight:700;padding:10px 28px;border-radius:4px;letter-spacing:1px;">Download Document</a>
                  </td>
                </tr>
              </table>

              <p style="margin:0;font-size:14px;color:#3a2010;">Warm regards,</p>
              <p style="margin:4px 0 0;font-size:15px;font-weight:700;color:#5c3a1e;">Team Anantya Foundation</p>

            </td>
          </tr>

          <!-- Colorful accent bar (bottom) -->
          <tr>
            <td style="height:5px;background:linear-gradient(to right,#9b59b6 20%,#5b9bd5 20% 40%,#6cbf6c 40% 60%,#f5c842 60% 80%,#e8923a 80%);"></td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#5c3a1e;padding:28px 48px;text-align:center;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:12px;">
                    <span style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#c8a97a;">Contact Us</span>
                  </td>
                </tr>
                <tr>
                  <td align="center">
                    <p style="margin:0 0 6px;font-size:13px;color:#e8d9c4;">
                      <a href="tel:+918076339730" style="color:#d4a96a;text-decoration:none;">+91 8076339730</a>
                    </p>
                    <p style="margin:0;font-size:13px;color:#e8d9c4;">
                      <a href="mailto:anantyafoundation03@gmail.com" style="color:#d4a96a;text-decoration:none;">anantyafoundation03@gmail.com</a>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>

        <p style="margin:20px 0 0;font-size:11px;color:#a08060;text-align:center;">This is an official communication from Anantya Foundation.</p>
      </td>
    </tr>
  </table>

</body>
</html>
    """

    message = MessageSchema(
        subject="Welcome to Anantya Foundation - Onboarding Complete",
        recipients=[member_data["email"]],
        body=body,
        subtype=MessageType.html,
    )

    await fm.send_message(message)
    print("Onboarding Mail sent!")