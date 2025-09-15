# routes/auth.py

import os

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from config.database import get_db
from controllers.auth import sign_in_failed, sign_in_success

router = APIRouter()

# OAuth configuration for Google
oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="auth_google_callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        # Prefer ID Token (OIDC) if available, otherwise fallback to userinfo endpoint
        userinfo = await oauth.google.parse_id_token(request, token)
        if not userinfo:
            resp = await oauth.google.get("userinfo", token=token)
            userinfo = resp.json()

        request.state.user = dict(userinfo)
        request.session["user_info"] = dict(userinfo)

        client_url = os.getenv("CLIENT_URL")
        if client_url:
            return RedirectResponse(url=client_url, status_code=302)
        return RedirectResponse(url=request.url_for("login_success"), status_code=302)
    except OAuthError:
        return RedirectResponse(url=request.url_for("login_failed"), status_code=302)


@router.get("/login/success", name="login_success")
async def login_success(request: Request, db: Session = Depends(get_db)):
    return await sign_in_success(request, db)


@router.get("/login/failed", name="login_failed")
async def login_failed(request: Request):
    return await sign_in_failed(request)