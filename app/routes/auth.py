from fastapi import APIRouter, HTTPException, status, Request
from app.models.schemas import AdminSignup, AdminLogin
import os
import uuid
import bcrypt
from dotenv import load_dotenv

from app.jwt_utils import create_access_token, verify_token
from fastapi import Depends


load_dotenv()

router = APIRouter()

ADMIN_SIGNUP_KEY = os.getenv('ADMIN_SINGUP_KEY')


@router.post('/admin_signup')
async def admin_signup(admin_data: AdminSignup, request: Request):

    # Validate signup key
    if admin_data.admin_signup_key != ADMIN_SIGNUP_KEY:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Signup Key')

    # Validate password confirmation
    if admin_data.password != admin_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    

    #check if a record for member_id exists
    check_member_admin = """
    SELECT * FROM members WHERE member_id = $1;
    """
    try:
        async with request.app.state.pool.acquire() as connection:
            # check if member exists
            member = await connection.fetchrow(
                check_member_admin,
                admin_data.member_id
            )

            if not member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid member_id. You must be a member first."
                )

            if member["is_admin"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are already an admin!"
                )

            s = bcrypt.gensalt()
            password_bytes = admin_data.password.encode('utf-8')
            password_hash = bcrypt.hashpw(password_bytes, s).decode('utf-8')

            print(password_hash)

            await connection.execute(
                """
                UPDATE members
                SET is_admin = TRUE
                WHERE member_id = $1
                """,
                admin_data.member_id
            )

            admin_id = str(uuid.uuid4())
            await connection.execute(
                """
                INSERT INTO admins(admin_id, member_id, password_hash, created_at)
                VALUES ($1, $2, $3, NOW())
                """,
                admin_id,
                admin_data.member_id,
                password_hash
            )

            return {"detail": "Admin signup successful", "admin_id": admin_id}

                            

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post('/admin_login')
async def admin_login(login_data: AdminLogin, request: Request):
    # convert the id to upper case
    login_data.member_id = login_data.member_id.upper()
    async with request.app.state.pool.acquire() as connection:
        admin = await connection.fetchrow(
            "SELECT * FROM admins WHERE member_id = $1", login_data.member_id
        )
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        password_bytes = login_data.password.encode('utf-8')
        stored_hash = admin["password_hash"].encode('utf-8')

        if not bcrypt.checkpw(password_bytes, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(data={"sub": str(admin["admin_id"])})
        return {"access_token": token, "token_type": "bearer"}


@router.get('/admin/dashboard')
async def admin_dashboard(token_payload: dict = Depends(verify_token)):
    return {"message": "Welcome admin", "admin_id": token_payload["sub"]}
