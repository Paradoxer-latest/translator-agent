# main.py

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from config.database import init_db
from routes.user import router as user_router
from routes.auth import router as auth_router


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB Connection
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# Session middleware (equivalent to express-session)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "SecretKey"),
    same_site="lax",
    https_only=False,
    session_cookie="session",
)

# Templates (Jinja2) and Static files
app.state.templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes
@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hey Ninja ! Go to /user/signin for the login page."

app.include_router(user_router, prefix="/user")
app.include_router(auth_router, prefix="/auth")

# Run server
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)