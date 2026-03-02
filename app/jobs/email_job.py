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
            "subject": "Welcome to Anantya Foundation 🎉",
            "html": f"""
            <html>
              <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#f4f4f4;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4; padding:20px;">
                  <tr>
                    <td align="center">
                      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; padding:30px; border-radius:8px;">
                        <tr>
                          <td align="center">
                            <h2 style="color:#333;">Welcome to Anantya Foundation 🎉</h2>
                            <p style="color:#555; font-size:16px;">
                              Your onboarding was successful!
                            </p>
                            <p style="font-size:18px;">
                              Your Unique ID:
                              <strong style="color:#2b6cb0;">{member_af_id}</strong>
                            </p>
                            <br/>

                            <br/><br/>
                            <p style="font-size:12px; color:#888;">
                              © 2026 Anantya Foundation. All rights reserved.
                            </p>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """
        })
        print("Mail Sent!", r)
    except Exception as e:
        print("Email failed:", str(e))