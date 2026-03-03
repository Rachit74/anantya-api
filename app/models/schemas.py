from pydantic import BaseModel, EmailStr

class OnboardingPost(BaseModel):
    email: EmailStr
    fullname: str
    age: int
    gender: str
    location: str
    phone_number: str
    profession: str
    place_of_profession: str
    department: str # change to list
    volunteered_before: str
    acknowledgement: bool