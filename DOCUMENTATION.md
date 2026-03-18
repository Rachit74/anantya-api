# Anantya Foundation API Documentation

A FastAPI-based backend for managing volunteer onboarding and administration for the Anantya Foundation.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Authentication](#authentication)
- [Services](#services)
- [Background Jobs](#background-jobs)
- [Configuration](#configuration)
- [Database Schema](#database-schema)

---

## Overview

Anantya Foundation API handles:

- **Member/Volunteer Onboarding**: Registration with comprehensive profile data
- **Member ID Generation**: Unique IDs using city codes (e.g., `AF-DEL-001`)
- **Admin Authentication**: Secure signup/login with rotating signup keys
- **Email Verification**: MX record-based email validation
- **Google Sheets Integration**: Automatic sync of member records
- **Admin Key Rotation**: Automatic generation and distribution of new signup keys

---

## Architecture

```
anantya-foundation-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── db.py                # PostgreSQL connection pool
│   ├── jwt_utils.py         # JWT token utilities
│   ├── limiter.py           # Rate limiting configuration
│   ├── data/
│   │   └── city_aliases.json    # City name to code mappings
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── routes/
│   │   ├── auth.py          # Admin authentication endpoints
│   │   └── members.py       # Member onboarding endpoints
│   ├── services/
│   │   ├── email_verifier.py   # Email validation service
│   │   └── id_generator.py     # Member ID generation
│   └── jobs/
│       ├── sheets_job.py    # Google Sheets sync job
│       └── key_gen.py       # Admin key rotation job
├── pyproject.toml           # Project dependencies
├── uv.lock                  # Dependency lock file
├── .env                     # Environment variables
├── gapi_creds.json          # Google API credentials (gitignored)
└── af-firebase-key.json     # Firebase credentials (gitignored)
```

### Technology Stack

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

---

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

---

## API Endpoints

### Member Endpoints

#### POST `/onboard`

Register a new member/volunteer.

**Rate Limit**: 3 requests per minute per IP

**Request Body**:
```json
{
  "email": "string",
  "fullname": "string",
  "age": "integer",
  "gender": "string",
  "location": "string",
  "phone_number": "string",
  "profession": "string",
  "place_of_profession": "string",
  "department": ["string"],
  "volunteered_before": "boolean",
  "acknowledgement": "boolean",
  "can_attend_events": "boolean",
  "government_id_picture": "string",
  "member_picture": "string",
  "dob": "YYYY-MM-DD"
}
```

**Response**: `200 OK` with success message

#### GET `/members`

Retrieve all members (protected endpoint).

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response**: `200 OK` with list of members

---

### Authentication Endpoints

#### POST `/admin_signup`

Register a new admin user.

**Request Body**:
```json
{
  "member_id": "string",
  "password": "string",
  "confirm_password": "string",
  "admin_signup_key": "string"
}
```

**Response**: `200 OK` with success message

#### POST `/admin_login`

Authenticate an admin user.

**Request Body**:
```json
{
  "member_id": "string",
  "password": "string"
}
```

**Response**: `200 OK` with JWT access token

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

#### GET `/admin/dashboard`

Access admin dashboard (protected).

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response**: `200 OK` with dashboard data

---

## Data Models

### Pydantic Schemas

#### `OnboardingPost`

Member registration data:

| Field | Type | Required |
|-------|------|----------|
| email | str | Yes |
| fullname | str | Yes |
| age | int | Yes |
| gender | str | Yes |
| location | str | Yes |
| phone_number | str | Yes |
| profession | str | Yes |
| place_of_profession | str | Yes |
| department | list[str] | Yes |
| volunteered_before | bool | Yes |
| acknowledgement | bool | Yes |
| can_attend_events | bool | Yes |
| government_id_picture | str | Yes |
| member_picture | str | Yes |
| dob | date | Yes |

#### `AdminSignup`

Admin registration data:

| Field | Type | Required |
|-------|------|----------|
| member_id | str | Yes |
| password | str | Yes |
| confirm_password | str | Yes |
| admin_signup_key | str | Yes |

#### `AdminLogin`

Admin login credentials:

| Field | Type | Required |
|-------|------|----------|
| member_id | str | Yes |
| password | str | Yes |

---

## Authentication

### JWT Authentication

- **Algorithm**: HS256
- **Token Expiration**: 60 minutes
- **Token URL**: `/auth/admin_login`

### Password Security

- Passwords hashed using **bcrypt**
- Per-password salt generation

### Admin Signup Key

Admin registration requires a valid signup key stored in the database:

1. Admin signs up with current signup key
2. Key is validated against database
3. New admin account created
4. Signup key automatically rotates
5. New key emailed to all existing admins

---

## Services

### Email Verifier (`app/services/email_verifier.py`)

Validates email addresses through:

1. **Syntax Validation**: Using `email-validator` library
2. **MX Record Check**: DNS lookup for mail exchange records
3. **Domain Verification**: Confirms domain accepts email

```python
from app.services.email_verifier import verify_email

is_valid = await verify_email("user@example.com")
```

### ID Generator (`app/services/id_generator.py`)

Generates unique member IDs:

- **Format**: `AF-CITYCODE-XXX`
- **Example**: `AF-DEL-001`
- **City Codes**: Derived from IATA airport codes
- **Counter Storage**: Firestore with atomic transactions

```python
from app.services.id_generator import generate_member_id

member_id = await generate_member_id("Delhi")
# Returns: "AF-DEL-001"
```

Supported cities are defined in `app/data/city_aliases.json`.

---

## Background Jobs

### Google Sheets Sync (`app/jobs/sheets_job.py`)

Syncs member data to Google Sheets:

- Triggered after successful member onboarding
- Runs as FastAPI BackgroundTask
- Uses `gspread` library for Sheets API

### Admin Key Rotation (`app/jobs/key_gen.py`)

Manages admin signup key rotation:

- Generates 16-character cryptographically secure key
- Updates key in database
- Emails new key to all admins
- Triggered after each admin signup

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET_KEY` | Secret for JWT signing | Yes |
| `MAIL_PASSWORD` | SMTP password for email | Yes |
| `FIREBASE_CREDS` | Firebase JSON (production) | No |
| `GOOGLE_CREDENTIALS` | Google API JSON (production) | No |

### Local Development Files

| File | Purpose |
|------|---------|
| `af-firebase-key.json` | Firebase service account (local) |
| `gapi_creds.json` | Google API credentials (local) |

### Database Connection Pool

Configured in `app/db.py`:

- **Minimum Connections**: 1
- **Maximum Connections**: 10
- **Connection Timeout**: 30 seconds

### CORS Configuration

Currently allows all origins (`*`). Restrict for production.

### Rate Limiting

- **Library**: SlowAPI
- **Default**: 3 requests/minute/IP for onboarding
- **Storage**: In-memory (consider Redis for production)

---

## Database Schema

### PostgreSQL Tables

#### `members`

Stores volunteer/member information:

| Column | Type | Description |
|--------|------|-------------|
| id | serial | Primary key |
| member_id | varchar | Unique member ID (AF-CITY-XXX) |
| email | varchar | Email address |
| fullname | varchar | Full name |
| age | integer | Age |
| gender | varchar | Gender |
| location | varchar | Location/city |
| phone_number | varchar | Phone number |
| profession | varchar | Profession |
| place_of_profession | varchar | Workplace |
| department | text[] | Departments (array) |
| volunteered_before | boolean | Previous volunteer experience |
| acknowledgement | boolean | Acknowledgement flag |
| can_attend_events | boolean | Event attendance capability |
| government_id_picture | varchar | Gov ID image URL |
| member_picture | varchar | Member photo URL |
| dob | date | Date of birth |
| created_at | timestamp | Record creation time |

#### `admins`

Stores admin credentials:

| Column | Type | Description |
|--------|------|-------------|
| id | serial | Primary key |
| member_id | varchar | FK to members.member_id |
| password_hash | varchar | bcrypt hashed password |
| email | varchar | Admin email |
| created_at | timestamp | Record creation time |

#### `keys`

Stores system keys:

| Column | Type | Description |
|--------|------|-------------|
| key_name | varchar | Key identifier (e.g., ADMIN_SIGNUP_KEY) |
| key_value | varchar | Current key value |
| updated_at | timestamp | Last update time |

### Firestore Collections

#### `city_counters`

Stores sequential counters per city:

```json
{
  "DEL": 1,
  "MUM": 5,
  "BLR": 10
}
```

Used for atomic ID generation.

---

## API Response Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing token |
| 422 | Validation Error - Invalid request body |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

---

## Development Notes

### Adding a New City

1. Add city mapping to `app/data/city_aliases.json`
2. City code should match IATA airport code

### Adding a New Endpoint

1. Create route in appropriate router (`app/routes/`)
2. Add Pydantic models in `app/models/schemas.py`
3. Add business logic in `app/services/` if complex
4. Apply rate limiting if needed

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

---

## Security Considerations

1. **CORS**: Currently permissive - restrict origins in production
2. **Rate Limiting**: Consider Redis-backed limiter for production
3. **Credentials**: Never commit credential files
4. **Key Rotation**: Admin signup keys rotate automatically after use
5. **Input Validation**: Email validation includes MX verification

---

## License

Proprietary - Anantya Foundation