from email_validator import validate_email, EmailNotValidError
import dns.resolver
from pydantic import EmailStr

def check_valid_email(email: EmailStr) -> bool:
    try:
        # 1. Validate syntax
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        return False

    # 2. Extract domain
    domain = email.split("@")[1]

    # 3. Check MX records
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        if len(mx_records) > 0:
            return True
    except:
        return False

    return False

