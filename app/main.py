from logging.config import dictConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .configs.log_config import LogConfig
from .routers import token, user, meeting, events
from .db import init_db_app_launch


dictConfig(LogConfig().dict())
app = FastAPI()

origins = [
    "http://0.0.0.0",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(token.router)
app.include_router(user.router)
app.include_router(meeting.router)
app.include_router(events.router)


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    init_db_app_launch(app)


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")


@app.get("/")
async def root():
    return {"message": "Hello World"}
