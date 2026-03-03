from fastapi import FastAPI, HTTPException, BackgroundTasks, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import uuid
from datetime import date
from contextlib import asynccontextmanager
import asyncpg

from .jobs import email_job
from .services import id_generator
from .db import create_db_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.pool = await create_db_pool()
    print("Database connected")

    yield  # App runs here

    # Shutdown
    await app.state.pool.close()
    print("Database connection closed")

app = FastAPI(lifespan=lifespan)



origins = [
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

class OnboardingPost(BaseModel):
    email: EmailStr
    fullname: str
    age: int
    gender: str
    location: str
    phone_number: str
    profession: str
    place_of_profession: str
    department: str
    volunteered_before: str
    acknowledgement: bool


"""
Method to handle the onboarding request body for new onboarding members
"""
@app.post('/onboard')
async def onboard(member: OnboardingPost, background_tasks: BackgroundTasks, request: Request):
    # mode.dump converts the pydatic data into json
    member_data = member.model_dump()
    member_data['email'] = member_data['email'].lower()
    member_data['uuid'] = str(uuid.uuid4())
    member_data['joining_date'] = date.today()

    member_af_id = id_generator.generate_unique_id(city=member_data['location'])

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

    background_tasks.add_task(email_job.send_mail, member=member_data)
    return {"id": result["id"], "member_id": member_data["member_id"]}

@app.get('/members')
async def get_members(request: Request):

    query = "SELECT * FROM members ORDER BY id DESC;"

    async with request.app.state.pool.acquire() as connection:
        rows = await connection.fetch(query)

    return [dict(row) for row in rows]