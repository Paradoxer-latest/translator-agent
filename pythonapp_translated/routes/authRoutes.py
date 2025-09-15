import os
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

from controllers.authController import googleSignInController

load_dotenv()

auth_router = APIRouter()

googleSignIn = googleSignInController()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@auth_router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url="/auth/login/failed")

    userinfo = token.get("userinfo")
    if not userinfo:
        try:
            # Try fetching user info explicitly if not included
            userinfo = await oauth.google.userinfo(token=token)
        except Exception:
            userinfo = None

    if not userinfo:
        return RedirectResponse(url="/auth/login/failed")

    # Store user info in session for the controller to use
    request.session["oauth_user"] = dict(userinfo)

    success_redirect = os.getenv("CLIENT_URL") or "/auth/login/success"
    return RedirectResponse(url=success_redirect)


@auth_router.get("/login/success")
async def login_success(request: Request):
    return await googleSignIn.signInSuccess(request)


@auth_router.get("/login/failed")
async def login_failed(request: Request):
    return googleSignIn.signInFailed(request)
