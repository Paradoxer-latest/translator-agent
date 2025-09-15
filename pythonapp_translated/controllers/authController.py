# controllers/auth.py

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import Response

from models.user import User


async def sign_in_success(request: Request, db: Session) -> Response:
    templates = request.app.state.templates

    # Retrieve user info added during Google OAuth callback
    user_data = (
        getattr(request.state, "user", None)
        or request.session.get("user")
        or request.session.get("user_info")
    )

    if not isinstance(user_data, dict):
        return JSONResponse(status_code=403, content={"error": True, "message": "Not Authorized"})

    email = (user_data.get("email") or "").strip().lower()
    name = (user_data.get("name") or user_data.get("given_name") or "").strip()
    sub = user_data.get("sub") or ""

    if not email:
        return JSONResponse(status_code=403, content={"error": True, "message": "Not Authorized"})

    user = db.query(User).filter(User.email == email).first()
    if user:
        request.session["userEmail"] = email
        return templates.TemplateResponse("homepage.html", {"request": request})

    # Create a new user if not found (store Google 'sub' as password, as in the original code)
    new_user = User(username=name or email.split("@")[0], email=email, password=sub)
    db.add(new_user)
    db.commit()

    request.session["userEmail"] = email
    return templates.TemplateResponse("homepage.html", {"request": request})


async def sign_in_failed(request: Request) -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": True, "message": "Log in failure"})