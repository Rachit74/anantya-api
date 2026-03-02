from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

from .jobs import send_mail


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
    phone_number: int
    profession: str
    place_of_profession: str
    department: str
    volunteered_before: str
    acknowledgement: bool


"""
Method to handle the onboarding request body for new onboarding members
"""
@app.post('/onboard')
async def onboard(member: OnboardingPost, background_task: BackgroundTasks):
    member = member.model_dump()
    member['Unique ID'] = uuid.uuid4()
    member['joining_date'] = datetime.now().date()

    background_task.add_task(send_mail, email=member["email"])
    return member