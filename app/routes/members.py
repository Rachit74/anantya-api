"""
Member Routes Module

This module defines the API endpoints for member management in the
Anantya Foundation volunteer system.

Endpoints:
    POST /onboard - Register a new member
    GET /members - Retrieve all registered members
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Request, Depends
from datetime import date
import uuid
import asyncpg

from app.models.schemas import OnboardingPost
from typing import List

from app.services.id_generator import generate_unique_id
from app.services.email_verifier import check_valid_email
from app.jobs.sheets_job import insert_member_record
from app.jwt_utils import verify_token

router = APIRouter()


@router.post('/onboard')
async def onboard(member: OnboardingPost, background_tasks: BackgroundTasks, request: Request):
    """
    Register a new member (volunteer) with the Anantya Foundation.

    This endpoint:
    1. Validates and processes the onboarding data
    2. Checks for duplicate email addresses
    3. Generates a unique member ID based on location
    4. Stores the member record in the database
    5. Returns the new member's UUID and member ID

    Args:
        member: OnboardingPost model containing all member details
        background_tasks: FastAPI background tasks (for email sending)
        request: Request object containing app state with DB pool

    Returns:
        dict: Contains 'uuid' and 'member_id' of the newly created member

    Raises:
        HTTPException: 400 if email already exists in the database
    """

    member_data = member.model_dump()
    member_data['email'] = member_data['email'].lower()
    member_data['uuid'] = str(uuid.uuid4())
    member_data['joining_date'] = date.today()
    member_data['government_id_picture'] = str(member_data['government_id_picture'])
    member_data['member_picture'] = str(member_data['member_picture'])

    # verfiy valid email
    is_valid_email = check_valid_email(member_data["email"])

    if not is_valid_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email")

    # Check for duplicate email
    email_check_query = "SELECT email FROM members WHERE email = $1;"

    try:
        async with request.app.state.pool.acquire() as connection:
            existing = await connection.fetchval(email_check_query, member_data['email'])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email Already exists",
                )
            
            member_af_id = generate_unique_id(city=member_data['location'])
            member_data['member_id'] = member_af_id

            query = """
            INSERT INTO members (
                uuid, email, fullname, age, gender, location,
                phone_number, profession, place_of_profession,
                department, volunteered_before, acknowledgement,
                can_attend_events, member_id, joining_date,
                government_id_picture, member_picture, dob
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18)
            RETURNING uuid;
            """

            result = await connection.fetchrow(
                query,
                member_data["uuid"],                    # $1
                member_data["email"],                    # $2
                member_data["fullname"],                 # $3
                member_data["age"],                      # $4
                member_data["gender"],                    # $5
                member_data["location"],                  # $6
                member_data["phone_number"],              # $7
                member_data["profession"],                # $8
                member_data["place_of_profession"],       # $9
                member_data["department"],                 # $10
                member_data["volunteered_before"],        # $11
                member_data["acknowledgement"],           # $12
                member_data["can_attend_events"],         # $13 (boolean)
                member_data["member_id"],                  # $14 (string)
                member_data["joining_date"],               # $15 (date)
                member_data["government_id_picture"],      # $16 (HttpUrl/string)
                member_data["member_picture"],              # $17 (HttpUrl/string)
                member_data["dob"],
            )

    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Already exists",
        )

    background_tasks.add_task(insert_member_record, member_data)
    # returning uuid, member_id (af specific) and fullname for nodemailer on frotnend
    return {"uuid": result["uuid"], "member_id": member_data["member_id"], "fullname": member_data["fullname"]}


@router.get('/members')
async def get_members(request: Request, token_payload: dict = Depends(verify_token)):
    """
    Retrieve all registered members.

    Returns a list of all members currently in the database,
    including their UUID, email, name, location, member ID,
    and email status.

    Args:
        request: Request object containing app state with DB pool

    Returns:
        List[MemberResponse]: List of member records
    """
    query = "SELECT * FROM members;"

    async with request.app.state.pool.acquire() as connection:
        rows = await connection.fetch(query)

    return [dict(row) for row in rows]