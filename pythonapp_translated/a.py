import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv

from config.mongodb import connectUsingMongoose
from routes.routes import router as user_router
from routes.authRoutes import auth_router

load_dotenv()

app = FastAPI()

# Sessions (similar to express-session)
app.add_middleware(
    SessionMiddleware,
    secret_key="SecretKey",
    same_site="lax",
    https_only=False,
)

# Static files (similar to express.static('public'))
if os.path.isdir("public"):
    app.mount("/public", StaticFiles(directory="public"), name="public")


@app.on_event("startup")
def startup_event():
    connectUsingMongoose()


@app.get("/")
def root():
    return PlainTextResponse("Hey Ninja ! Go to /user/signin for the login page.")


# Routers (similar to app.use('/user', router) and app.use('/auth', authrouter))
app.include_router(user_router, prefix="/user")
app.include_router(auth_router, prefix="/auth")
