"""
Member Routes Module - SQLAlchemy ORM version
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import date
import uuid

from app.models.schemas import OnboardingPost
from app.models.models import Member                    # your new models.py
from app.db import get_db                            # your new db.py
from app.services.id_generator import generate_unique_id
from app.services.email_verifier import check_valid_email
from app.jobs.sheets_job import insert_member_record
from app.jwt_utils import verify_token
from app.limiter import limiter

router = APIRouter()


@router.post('/onboard')
@limiter.limit("3/minute")
async def onboard(
    member: OnboardingPost,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db)          # ← replaces pool.acquire()
):
    member_data = member.model_dump()
    member_data['email'] = member_data['email'].lower()
    member_data['government_id_picture'] = str(member_data['government_id_picture'])
    member_data['member_picture'] = str(member_data['member_picture'])

    # Validate email
    if not check_valid_email(member_data['email']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email")

    # Check for duplicate email using ORM
    result = await db.execute(
        select(Member).where(Member.email == member_data['email'])
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Generate IDs
    member_uuid = str(uuid.uuid4())
    member_id = generate_unique_id()

    # Build ORM object — maps directly to your Member model columns
    new_member = Member(
        uuid=member_uuid,
        member_id=member_id,
        email=member_data['email'],
        fullname=member_data['fullname'],
        age=member_data['age'],
        gender=member_data['gender'],
        dob=member_data['dob'],
        location=member_data['location'],
        phone_number=member_data['phone_number'],
        profession=member_data['profession'],
        place_of_profession=member_data['place_of_profession'],
        department=member_data['department'],           # list → ARRAY(String) 
        volunteered_before=member_data['volunteered_before'],
        acknowledgement=member_data['acknowledgement'],
        can_attend_events=member_data['can_attend_events'],
        government_id_picture=member_data['government_id_picture'],
        member_picture=member_data['member_picture'],
        joining_date=date.today(),
    )

    try:
        db.add(new_member)
        await db.commit()
        await db.refresh(new_member)        # loads DB-generated values back
    except IntegrityError:
        await db.rollback()                 # always rollback on failure
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Pass member_data to background task (sheets sync)
    member_data['uuid'] = str(member_uuid)
    member_data['member_id'] = member_id
    member_data['joining_date'] = date.today()
    background_tasks.add_task(insert_member_record, member_data)

    return {
        "uuid": str(new_member.uuid),
        "member_id": new_member.member_id,
        "fullname": new_member.fullname
    }


@router.get('/members')
async def get_members(
    db: AsyncSession = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    result = await db.execute(select(Member))
    members = result.scalars().all()
    return members
