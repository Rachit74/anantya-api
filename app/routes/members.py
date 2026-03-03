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
    # mode.dump converts the pydatic data into json
    member_data = member.model_dump()
    member_data['email'] = member_data['email'].lower()
    member_data['uuid'] = str(uuid.uuid4())
    member_data['joining_date'] = date.today()

    member_af_id = generate_unique_id(city=member_data['location'])

    member_data['member_id'] = member_af_id

    query = """
    INSERT INTO members (
        uuid, email, fullname, age, gender, location,
        phone_number, profession, place_of_profession,
        department, volunteered_before, acknowledgement,
        member_id, joining_date
    )
    VALUES (
        $1,$2,$3,$4,$5,$6,
        $7,$8,$9,$10,$11,$12,
        $13,$14
    )
    RETURNING id;
    """

    try:
        async with request.app.state.pool.acquire() as connection:
            result = await connection.fetchrow(
                query,
                member_data["uuid"],
                member_data["email"],
                member_data["fullname"],
                member_data["age"],
                member_data["gender"],
                member_data["location"],
                member_data["phone_number"],
                member_data["profession"],
                member_data["place_of_profession"],
                member_data["department"],
                member_data["volunteered_before"],
                member_data["acknowledgement"],
                member_data["member_id"],
                member_data["joining_date"],
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