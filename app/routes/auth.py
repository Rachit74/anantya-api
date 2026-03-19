from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks, Depends, Response
from app.models.schemas import AdminSignup, AdminLogin
import uuid
import bcrypt

from app.jwt_utils import create_access_token, verify_token
from app.jobs.key_gen import rotate_admin_signup_key
from app.jobs.password_reset_token import update_token

router = APIRouter()


@router.post('/admin_signup')
async def admin_signup(admin_data: AdminSignup, request: Request, background_tasks: BackgroundTasks):
    admin_data.member_id = admin_data.member_id.upper()

    # Validate password confirmation early, before any DB calls
    if admin_data.password != admin_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    try:
        async with request.app.state.pool.acquire() as connection:

            # Fetch signup key from DB
            key_row = await connection.fetchrow(
                "SELECT key_value FROM keys WHERE key_name = 'ADMIN_SIGNUP_KEY';"
            )

            if not key_row:
                raise HTTPException(status_code=500, detail="Signup key not configured")

            if admin_data.admin_signup_key != key_row["key_value"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Signup Key')

            # Check if member exists
            member = await connection.fetchrow(
                "SELECT * FROM members WHERE member_id = $1;",
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
            password_hash = bcrypt.hashpw(admin_data.password.encode('utf-8'), s).decode('utf-8')

            await connection.execute(
                "UPDATE members SET is_admin = TRUE WHERE member_id = $1",
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

            # All checks passed and INSERT succeeded — now safe to rotate the key
            background_tasks.add_task(rotate_admin_signup_key, request.app.state.pool, admin_data)
            return {"detail": "Admin signup successful", "admin_id": admin_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/admin_login')
async def admin_login(login_data: AdminLogin, request: Request):
    login_data.member_id = login_data.member_id.upper()

    async with request.app.state.pool.acquire() as connection:
        admin = await connection.fetchrow(
            "SELECT * FROM admins WHERE member_id = $1", login_data.member_id
        )
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not bcrypt.checkpw(login_data.password.encode('utf-8'), admin["password_hash"].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(data={"sub": str(admin["admin_id"])})
        return {"access_token": token, "token_type": "bearer"}


@router.get('/admin/dashboard')
async def admin_dashboard(token_payload: dict = Depends(verify_token)):
    return {"message": "Welcome admin", "admin_id": token_payload["sub"]}


@router.get('/password_reset_token')
async def password_reset_token(member_email: str, request: Request, background_tasks: BackgroundTasks):
    member_email = member_email.lower()
    try:
        async with request.app.state.pool.acquire() as connection:
            member = await connection.fetchrow("SELECT email, uuid, is_admin FROM members WHERE email = $1;", member_email)

        if not member:
            print("No Account Found with the email")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Account Found for the email!")
        
        if member['is_admin'] == False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email is not registered as admin!")


        # background task which will create a token and send it as an email
        background_tasks.add_task(update_token, request.app.state.pool, dict(member))

        return Response(content="You’ll receive an email with a link to reset your password.", status_code=status.HTTP_200_OK)
    

    
    except HTTPException:
        raise