from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
import uuid
import bcrypt
from datetime import datetime, timezone

from app.models.schemas import AdminSignup, AdminLogin
from app.models.models import Admin, Member, Key
from app.db import get_db
from app.jwt_utils import create_access_token, verify_token
from app.jobs.key_gen import rotate_admin_signup_key

router = APIRouter()


@router.post('/admin_signup')
async def admin_signup(
    admin_data: AdminSignup,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    admin_data.member_id = admin_data.member_id.upper()

    if admin_data.password != admin_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    try:
        # Fetch signup key
        key_result = await db.execute(
            select(Key).where(Key.key_name == 'ADMIN_SIGNUP_KEY')
        )
        key_row = key_result.scalar_one_or_none()

        if not key_row:
            raise HTTPException(status_code=500, detail="Signup key not configured")

        if admin_data.admin_signup_key != key_row.key_value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Signup Key')

        # Check member exists
        member_result = await db.execute(
            select(Member).where(Member.member_id == admin_data.member_id)
        )
        member = member_result.scalar_one_or_none()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid member_id. You must be a member first."
            )

        if member.is_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already an admin!"
            )

        # Hash password
        password_hash = bcrypt.hashpw(
            admin_data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Promote member to admin
        member.is_admin = True

        # Create admin record
        new_admin = Admin(
            admin_id=str(uuid.uuid4()),
            member_id=admin_data.member_id,
            password_hash=password_hash,
            created_at=datetime.now(timezone.utc)
        )

        db.add(new_admin)
        await db.commit()
        await db.refresh(new_admin)

        # Rotate key only after successful commit
        background_tasks.add_task(rotate_admin_signup_key, db, admin_data)

        return {"detail": "Admin signup successful", "admin_id": str(new_admin.admin_id)}

    except HTTPException:
        raise
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Admin already exists")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/admin_login')
async def admin_login(
    login_data: AdminLogin,
    db: AsyncSession = Depends(get_db)
):
    login_data.member_id = login_data.member_id.upper()

    result = await db.execute(
        select(Admin).where(Admin.member_id == login_data.member_id)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(login_data.password.encode('utf-8'), admin.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(admin.admin_id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get('/admin/dashboard')
async def admin_dashboard(token_payload: dict = Depends(verify_token)):
    return {"message": "Welcome admin", "admin_id": token_payload["sub"]}