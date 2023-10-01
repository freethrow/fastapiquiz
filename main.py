import contextlib

import uvicorn
from decouple import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from routers.players import router as players_router

DB_URL = config("DB_URL", cast=str)
DB_NAME = config("DB_NAME", cast=str)


# define origins
origins = ["*"]


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup")
    yield
    print("shutdown")


# instantiate the app
app = FastAPI(root_path="/", lifespan=lifespan)

# add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(
        "mongodb+srv://nbaquiz:nbaquiz@freethrow.o2qu3.mongodb.net/?retryWrites=true&w=majority"
    )
    app.mongodb = app.mongodb_client["nbaquiz"]

    from pymongo.errors import ConnectionFailure

    try:
        # The ping command is cheap and does not require auth.
        app.mongodb_client.admin.command("ping")
        print("Ping ok!")
    except ConnectionFailure:
        print("Server not available")


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(players_router, prefix="/players", tags=["players"])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
