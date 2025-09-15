# controllers/controller.py

import os
import secrets

import bcrypt
from aiosmtplib import SMTP
from email.message import EmailMessage
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import Response


from models.user import User


async def get_sign_up_page(request: Request) -> Response:
    templates = request.app.state.templates
    return templates.TemplateResponse("signup.html", {"request": request, "message": ""})


async def get_sign_in_page(request: Request) -> Response:
    templates = request.app.state.templates
    return templates.TemplateResponse("signin.html", {"request": request, "message": ""})


async def home_page(request: Request) -> Response:
    templates = request.app.state.templates
    email = request.session.get("userEmail")
    if not email:
        return templates.TemplateResponse(
            "signin.html",
            {"request": request, "message": "Please sign in to view the homepage"},
            status_code=404,
        )
    return templates.TemplateResponse("homepage.html", {"request": request})


async def get_forgot_password(request: Request) -> Response:
    templates = request.app.state.templates
    return templates.TemplateResponse("forgot-password.html", {"request": request, "message": ""})


async def get_change_password(request: Request) -> Response:
    templates = request.app.state.templates
    email = request.session.get("userEmail")
    if not email:
        return templates.TemplateResponse(
            "signin.html",
            {"request": request, "message": "Please sign in to change the password"},
            status_code=404,
        )
    return templates.TemplateResponse("change-password.html", {"request": request, "message": ""})


async def logout_user(request: Request) -> Response:
    templates = request.app.state.templates
    try:
        request.session.clear()
        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "user logout"}, status_code=201
        )
    except Exception as exc:
        print("Error signing out:", exc)
        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "Error signing out"}, status_code=500
        )


# POST handlers

async def create_user(request: Request, db: Session) -> Response:
    templates = request.app.state.templates
    form = await request.form()
    username = (form.get("username") or "").strip()
    email = (form.get("email") or "").strip().lower()
    password = form.get("password") or ""
    cpassword = form.get("cpassword") or ""

    if password != cpassword:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "message": "Passwords don't match"}, status_code=400
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "message": "User already exists"}, status_code=400
        )

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(username=username, email=email, password=hashed_password)

    try:
        db.add(user)
        db.commit()
        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "User created successfully"}, status_code=201
        )
    except IntegrityError as exc:
        db.rollback()
        return templates.TemplateResponse(
            "signup.html", {"request": request, "message": "User already exists"}, status_code=409
        )
    except Exception as exc:
        db.rollback()
        return templates.TemplateResponse(
            "signup.html", {"request": request, "message": str(exc)}, status_code=409
        )


async def sign_in_user(request: Request, db: Session) -> Response:
    templates = request.app.state.templates
    form = await request.form()
    email = (form.get("email") or "").strip().lower()
    password = form.get("password") or ""
    recaptcha = form.get("g-recaptcha-response")

    if recaptcha in (None, "", "null"):
        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "Please select captcha"}, status_code=404
        )

    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if not existing_user:
            return templates.TemplateResponse(
                "signin.html", {"request": request, "message": "User doesn't exist"}, status_code=404
            )

        is_password_correct = bcrypt.checkpw(
            password.encode("utf-8"), existing_user.password.encode("utf-8")
        )
        if not is_password_correct:
            return templates.TemplateResponse(
                "signin.html",
                {"request": request, "message": "Invalid credentials || Incorrect Password"},
                status_code=400,
            )

        request.session["userEmail"] = email
        return RedirectResponse(url="/user/homepage", status_code=302)

    except Exception as exc:
        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": str(exc)}, status_code=500
        )


async def forgot_password(request: Request, db: Session) -> Response:
    templates = request.app.state.templates
    form = await request.form()
    email = (form.get("email") or "").strip().lower()

    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if not existing_user:
            return templates.TemplateResponse(
                "forgot-password.html", {"request": request, "message": "User doesn't exist"}, status_code=404
            )

        # Generate a random 8-character password
        new_password = secrets.token_urlsafe(6)[:8]
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Send email with the new password
        try:
            await _send_password_reset_email(to_email=email, new_password=new_password)
        except Exception as exc:
            print(exc)
            return templates.TemplateResponse(
                "forgot-password.html",
                {"request": request, "message": f"Not valid Email{exc}"},
                status_code=404,
            )

        existing_user.password = hashed_password
        db.add(existing_user)
        db.commit()

        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "New Password sent to your email"}, status_code=201
        )

    except Exception as exc:
        db.rollback()
        return templates.TemplateResponse(
            "forgot-password.html", {"request": request, "message": str(exc)}, status_code=500
        )


async def change_password(request: Request, db: Session) -> Response:
    templates = request.app.state.templates
    form = await request.form()
    old_password = form.get("oldPassword") or ""
    new_password = form.get("newPassword") or ""

    try:
        email = request.session.get("userEmail")
        existing_user = db.query(User).filter(User.email == email).first() if email else None
        if not existing_user:
            return templates.TemplateResponse(
                "change-password.html", {"request": request, "message": "User doesn't exist"}, status_code=404
            )

        is_password_correct = bcrypt.checkpw(
            old_password.encode("utf-8"), existing_user.password.encode("utf-8")
        )
        if not is_password_correct:
            return templates.TemplateResponse(
                "change-password.html", {"request": request, "message": "Invalid credentials"}, status_code=400
            )

        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        existing_user.password = hashed_password
        db.add(existing_user)
        db.commit()

        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "Password changed successfully"}, status_code=201
        )

    except Exception as exc:
        db.rollback()
        return templates.TemplateResponse(
            "change-password.html", {"request": request, "message": str(exc)}, status_code=500
        )


# Helpers

async def _send_password_reset_email(to_email: str, new_password: str) -> None:
    """
    Send a password reset email using aiosmtplib.
    Expects the following environment variables:
    - EMAIL: SMTP username/sender email
    - EMAIL_PASSWORD: SMTP password or app password
    - SMTP_HOST: SMTP server host (default: smtp.gmail.com)
    - SMTP_PORT: SMTP port (default: 587)
    """
    sender = os.getenv("EMAIL", "")
    password = os.getenv("EMAIL_PASSWORD", "")
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))

    if not sender or not password:
        raise RuntimeError("Email credentials are not configured")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = "Password Reset"
    msg.set_content(f"Your new password is: {new_password}")

    async with SMTP(hostname=host, port=port, start_tls=True) as smtp:
        await smtp.connect()
        await smtp.starttls()
        await smtp.login(sender, password)
        await smtp.send_message(msg)