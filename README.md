# Anantya Foundation API

A FastAPI-based backend for managing volunteer onboarding and administration for the Anantya Foundation.

## Features

- **Member/Volunteer Onboarding** - Registration with comprehensive profile data
- **Member ID Generation** - Unique IDs using Joining Date in the dd/mm/yy format (e.g., `AF-300426-001`)
- **Admin Authentication** - Secure signup/login with rotating signup keys
- **Email Verification** - MX record-based email validation
- **Google Sheets Integration** - Automatic sync of member records
- **Admin Key Rotation** - Automatic generation and distribution of new signup keys

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL (asyncpg) |
| NoSQL | Firestore (Firebase Admin) |
| Authentication | JWT (python-jose), bcrypt |
| Rate Limiting | SlowAPI |
| Email Services | Resend, SendGrid, Brevo |
| Google Integration | gspread (Google Sheets) |
| Package Manager | uv |

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── db.py                # PostgreSQL connection pool
├── jwt_utils.py         # JWT token utilities
├── limiter.py           # Rate limiting configuration
├── data/
│   └── city_aliases.json    # City name to code mappings
├── models/
│   ├── models.py        # SQLAlchemy models
│   └── schemas.py       # Pydantic request/response models
├── routes/
│   ├── auth.py          # Admin authentication endpoints
│   └── members.py       # Member onboarding endpoints
├── services/
│   ├── email_verifier.py    # Email validation service
│   └── id_generator.py      # Member ID generation
└── jobs/
    ├── sheets_job.py        # Google Sheets sync job
    ├── key_gen.py           # Admin key rotation job
    ├── onboarding_email.py  # Onboarding email job
    └── password_reset_token.py
```

## Getting Started

### Prerequisites

- Python 3.14+
- PostgreSQL database
- Firebase project (for Firestore)
- Google Cloud project (for Sheets API)

### Installation

```bash
# Install dependencies using uv
uv sync

# Or using pip
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file with the following variables:

```env
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-secret-key
MAIL_PASSWORD=your-email-password
FIREBASE_CREDS={"type":"service_account",...}  # JSON string for production
GOOGLE_CREDENTIALS={"type":"service_account",...}  # JSON string for production
```

For local development, place credential files:
- `af-firebase-key.json` - Firebase service account
- `gapi_creds.json` - Google API credentials

### Running the Server

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Member Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/onboard` | Register a new member/volunteer |
| GET | `/members` | Retrieve all members (protected) |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin_signup` | Register a new admin user |
| POST | `/admin_login` | Authenticate an admin user |
| GET | `/admin/dashboard` | Access admin dashboard (protected) |

## Database Schema

### PostgreSQL Tables

- **members** - Stores volunteer/member information
- **admins** - Stores admin credentials
- **keys** - Stores system keys (e.g., ADMIN_SIGNUP_KEY)

### Firestore Collections

- **city_counters** - Sequential counters per city for ID generation

## Security

- Passwords hashed using bcrypt
- JWT tokens with 60-minute expiration
- Admin signup key rotation after each use
- Email validation with MX verification
- Rate limiting on onboarding endpoint (3 requests/minute/IP)

## License

Proprietary - Anantya Foundation