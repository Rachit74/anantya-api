from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime, date, time, timedelta, timezone


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
    email: str
    fullname: str
    age: int
    gender: str
    location: str
    phone_number: int
    profession: str
    place_of_profession: str
    department: str
    volunteered_before: str

@app.post('/onboard')
def onboard(member: OnboardingPost):
    member = member.model_dump()
    member['Unique ID'] = uuid.uuid4()
    member['joining_date'] = datetime.now().date()
    return member
