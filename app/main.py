from fastapi import FastAPI, Response, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_db_pool
from app.routes import members


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.pool = await create_db_pool()
        print("DATABASE CONNECTED")
        yield
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise
    finally:
        if hasattr(app.state, 'pool'):
            await app.state.pool.close()
            print("DB CONNECTION CLOSED")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router)

@app.get('/')
def home():
    return Response('API UP', status_code=status.HTTP_200_OK)