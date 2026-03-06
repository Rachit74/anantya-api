from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List
from datetime import date

class OnboardingPost(BaseModel):
    email: EmailStr
    fullname: str
    age: int
    gender: str
    location: str
    phone_number: str
    profession: str
    place_of_profession: str
    department: List[str]
    volunteered_before: str
    acknowledgement: bool
    can_attend_events: bool
    government_id_picture: HttpUrl
    member_picture: HttpUrl
    dob: date

class MemberResponse(BaseModel):
    email: EmailStr
    fullname: str
    location: str
    member_id: str
    email_sent: bool
    # uuid (to be removed later)
    uuid: str