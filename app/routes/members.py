from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Request
from datetime import date
import uuid
import asyncpg

from app.models.schemas import OnboardingPost
from app.jobs.email_job import send_mail
from app.services.id_generator import generate_unique_id

router = APIRouter()

"""
Method to handle the onboarding request body for new onboarding members
"""
@router.post('/onboard')
async def onboard(member: OnboardingPost, background_tasks: BackgroundTasks, request: Request):
    member_data = member.model_dump()
    member_data['email'] = member_data['email'].lower()
    member_data['uuid'] = str(uuid.uuid4())
    member_data['joining_date'] = date.today()
    member_data['government_id_picture'] = str(member_data['government_id_picture'])
    member_data['member_picture'] = str(member_data['member_picture'])

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
                government_id_picture, member_picture
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)
            RETURNING id;
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
                member_data["member_picture"]              # $17 (HttpUrl/string)
            )

    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Already exists",
        )

    background_tasks.add_task(send_mail, member=member_data)
    return {"id": result["id"], "member_id": member_data["member_id"]}

@router.get('/members')
async def get_members(request: Request):

    query = "SELECT * FROM members ORDER BY id DESC;"

    async with request.app.state.pool.acquire() as connection:
        rows = await connection.fetch(query)

    return [dict(row) for row in rows]