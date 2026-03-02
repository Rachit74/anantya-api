from fastapi import FastAPI, HTTPException, BackgroundTasks, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime, date
# from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from .jobs import email_job
from .services.services import gen_af_id
from .db import members_collection

app = FastAPI()


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
async def onboard(member: OnboardingPost, background_tasks: BackgroundTasks):
    # mode.dump converts the pydatic data into json
    member = member.model_dump()
    member['email'] = member['email'].lower()
    member['Unique ID'] = str(uuid.uuid4())
    member['joining_date'] = date.today().isoformat()

    member_af_id = gen_af_id(city=member['location'])

    member['member_id'] = member_af_id

    try:
        await members_collection.insert_one(member)
    except DuplicateKeyError:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Already exists",
        )

    background_tasks.add_task(email_job.send_mail, email=member["email"], member_af_id=member_af_id)
    return Response(status_code=status.HTTP_201_CREATED)

@app.get('/members')
async def get_members():
    cursor = members_collection.find({})

    members = await cursor.to_list(length=1000)

    # Convert _id to string
    for m in members:
        m['_id'] = str(m['_id'])

    return members