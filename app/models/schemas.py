"""
Pydantic Models for Request/Response Validation

This module defines the data models used for validating and
serializing API request bodies and responses.

Models:
    OnboardingPost: Request body for new member registration
    MemberResponse: Response model for member data retrieval
"""

from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List
from datetime import date


class OnboardingPost(BaseModel):
    """
    Request model for new member onboarding.

    Captures all required information for registering a new volunteer
    with the Anantya Foundation.

    Attributes:
        email: Member's email address (validated format)
        fullname: Member's full name
        age: Member's age in years
        gender: Member's gender
        location: City/locality string (format: "City, Locality" or "City")
        phone_number: Contact phone number
        profession: Member's occupation
        place_of_profession: Workplace or institution
        department: List of departments member wants to join
        volunteered_before: Previous volunteering experience
        acknowledgement: Member's agreement to terms
        can_attend_events: Availability for events
        government_id_picture: URL to government ID image
        member_picture: URL to member's photo
        dob: Date of birth
    """
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



class AdminSignup(BaseModel):
    member_id: str
    password: str
    confirm_password: str
    admin_signup_key: str

class AdminLogin(BaseModel):
    member_id: str
    password: str