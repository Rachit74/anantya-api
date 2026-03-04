from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

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
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Welcome to Anantya Foundation</title>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&display=swap" rel="stylesheet"/>
    </head>
    <body style="margin:0;padding:0;background-color:#f4f1eb;font-family:'DM Sans','Trebuchet MS',Arial,sans-serif;">

      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f1eb;padding:40px 20px;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:4px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

              <!-- Header -->
              <tr>
                <td style="background-color:#2c5f2e;padding:40px 48px 32px;text-align:center;">
                  <p style="margin:0 0 8px;font-family:'DM Sans',Arial,sans-serif;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#a8d5a2;">Est. with Purpose</p>
                  <h1 style="margin:0;font-family:'DM Serif Display','Georgia',serif;font-size:32px;font-weight:normal;color:#ffffff;letter-spacing:1px;">Anantya Foundation</h1>
                  <div style="margin:20px auto 0;width:48px;height:2px;background-color:#a8d5a2;"></div>
                </td>
              </tr>

              <!-- Welcome Banner -->
              <tr>
                <td style="background-color:#e8f5e9;padding:24px 48px;text-align:center;border-bottom:1px solid #d4edda;">
                  <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:13px;letter-spacing:3px;text-transform:uppercase;color:#2c5f2e;">Welcome Aboard</p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:40px 48px;">

                  <p style="margin:0 0 20px;font-size:16px;line-height:1.7;color:#333333;">Dear <strong>{member['fullname']}</strong>,</p>

                  <p style="margin:0 0 24px;font-size:15px;line-height:1.8;color:#555555;">
                    We are pleased to confirm your onboarding as a volunteer with Anantya Foundation. Your decision to contribute your time and effort toward community service is deeply valued, and we look forward to your active participation.
                  </p>

                  <!-- Volunteer ID Box -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                    <tr>
                      <td style="background-color:#f4f9f4;border:1px solid #c3dfc5;border-left:4px solid #2c5f2e;border-radius:4px;padding:20px 24px;">
                        <p style="margin:0 0 6px;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#2c5f2e;">Your Unique Volunteer ID</p>
                        <p style="margin:0;font-size:24px;font-weight:bold;color:#1a3d1c;letter-spacing:2px;font-family:'Courier New',monospace;">{member['member_id']}</p>
                        <p style="margin:8px 0 0;font-size:12px;color:#777777;line-height:1.5;">Kindly use this ID in all communications, event registrations, attendance submissions, and reports.</p>
                      </td>
                    </tr>
                  </table>

                  <!-- Guidelines -->
                  <p style="margin:0 0 16px;font-size:13px;letter-spacing:2px;text-transform:uppercase;color:#2c5f2e;font-family:'DM Sans',Arial,sans-serif;font-weight:700;">As Part of Your Onboarding</p>

                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <!-- Guideline 1 -->
                    <tr>
                      <td style="padding:12px 0;border-bottom:1px solid #f0f0f0;vertical-align:top;">
                        <table cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="width:28px;vertical-align:top;padding-top:2px;">
                              <div style="width:20px;height:20px;background-color:#2c5f2e;border-radius:50%;text-align:center;line-height:20px;font-size:11px;color:#ffffff;font-family:Arial,sans-serif;">1</div>
                            </td>
                            <td style="font-size:14px;line-height:1.7;color:#444444;padding-left:12px;">
                              Maintain <strong>professionalism and punctuality</strong> during all activities.
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <!-- Guideline 2 -->
                    <tr>
                      <td style="padding:12px 0;border-bottom:1px solid #f0f0f0;vertical-align:top;">
                        <table cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="width:28px;vertical-align:top;padding-top:2px;">
                              <div style="width:20px;height:20px;background-color:#2c5f2e;border-radius:50%;text-align:center;line-height:20px;font-size:11px;color:#ffffff;font-family:Arial,sans-serif;">2</div>
                            </td>
                            <td style="font-size:14px;line-height:1.7;color:#444444;padding-left:12px;">
                              Follow the <strong>guidance of your assigned team lead</strong>.
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <!-- Guideline 3 -->
                    <tr>
                      <td style="padding:12px 0;border-bottom:1px solid #f0f0f0;vertical-align:top;">
                        <table cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="width:28px;vertical-align:top;padding-top:2px;">
                              <div style="width:20px;height:20px;background-color:#2c5f2e;border-radius:50%;text-align:center;line-height:20px;font-size:11px;color:#ffffff;font-family:Arial,sans-serif;">3</div>
                            </td>
                            <td style="font-size:14px;line-height:1.7;color:#444444;padding-left:12px;">
                              Represent the foundation <strong>responsibly in public and on social media</strong>.
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <!-- Guideline 4 -->
                    <tr>
                      <td style="padding:12px 0;vertical-align:top;">
                        <table cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="width:28px;vertical-align:top;padding-top:2px;">
                              <div style="width:20px;height:20px;background-color:#2c5f2e;border-radius:50%;text-align:center;line-height:20px;font-size:11px;color:#ffffff;font-family:Arial,sans-serif;">4</div>
                            </td>
                            <td style="font-size:14px;line-height:1.7;color:#444444;padding-left:12px;">
                              Submit <strong>event photos, videos, and reports</strong> within the given deadlines.
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <p style="margin:0 0 24px;font-size:14px;line-height:1.8;color:#555555;">
                    You will soon receive updates regarding upcoming events, project allocations, and reporting structure. Stay active on official communication channels to avoid missing important announcements.
                  </p>

                  <p style="margin:0 0 32px;font-size:14px;line-height:1.8;color:#555555;">
                    For any queries, feel free to reach out to us. We look forward to your meaningful contribution.
                  </p>

                  <p style="margin:0;font-size:14px;color:#333333;font-family:'DM Sans',Arial,sans-serif;">Warm regards,</p>
                  <p style="margin:4px 0 0;font-size:15px;font-weight:700;color:#2c5f2e;font-family:'DM Sans',Arial,sans-serif;">Team Anantya Foundation</p>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background-color:#2c5f2e;padding:28px 48px;text-align:center;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td align="center" style="padding-bottom:12px;">
                        <span style="margin:0 12px;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#a8d5a2;">Contact Us</span>
                      </td>
                    </tr>
                    <tr>
                      <td align="center">
                        <p style="margin:0 0 6px;font-size:13px;color:#d4edda;">
                          📞 <a href="tel:+918076339730" style="color:#a8d5a2;text-decoration:none;">+91 8076339730</a>
                        </p>
                        <p style="margin:0;font-size:13px;color:#d4edda;">
                          ✉️ <a href="mailto:anantyafoundation03@gmail.com" style="color:#a8d5a2;text-decoration:none;">anantyafoundation03@gmail.com</a>
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

            </table>

            <!-- Sub-footer note -->
            <p style="margin:20px 0 0;font-size:11px;color:#999999;text-align:center;">This is an official communication from Anantya Foundation.</p>

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
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    print("Mail Sent!")