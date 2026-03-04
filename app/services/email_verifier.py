import httpx
from pydantic import EmailStr

async def rapid_email_verifier(email: EmailStr) -> dict:
    """
    Verify email using the free Rapid Email Verifier API
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://rapid-email-verifier.fly.dev/api/validate",
            params={"email": email}
        )
        return response.json()