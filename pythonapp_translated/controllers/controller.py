import os
import bcrypt
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from models.userModel import User
from config.nodemailerConfig import transporter


# Configure Jinja2 templates directory (converted from EJS to Jinja2)
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "views")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class UserGetController:
    def getSignUpPage(self, request: Request):
        return templates.TemplateResponse("signup.html", {"request": request, "message": ""})

    def getSignInPage(self, request: Request):
        return templates.TemplateResponse("signin.html", {"request": request, "message": ""})

    def homePage(self, request: Request):
        email = request.session.get("user_email")
        if not email:
            return templates.TemplateResponse(
                "signin.html",
                {"request": request, "message": "Please sign in to view the homepage"},
                status_code=404,
            )
        return templates.TemplateResponse("homepage.html", {"request": request})

    def getForgotPassword(self, request: Request):
        return templates.TemplateResponse("forgot-password.html", {"request": request, "message": ""})

    def getChangePassword(self, request: Request):
        email = request.session.get("user_email")
        if not email:
            return templates.TemplateResponse(
                "signin.html",
                {"request": request, "message": "Please sign in to change the password"},
                status_code=404,
            )
        return templates.TemplateResponse("change-password.html", {"request": request, "message": ""})

    def logoutUser(self, request: Request):
        request.session.clear()
        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "user logout"}, status_code=201
        )


class UserPostController:
    # sign up
    async def createUser(self, request: Request, *, username: str, email: str, password: str, cpassword: str):
        if password != cpassword:
            return templates.TemplateResponse(
                "signup.html", {"request": request, "message": "Passwords don't match"}, status_code=400
            )

        # check if user already exists
        existing_user = User.objects(email=email).first()
        if existing_user:
            return templates.TemplateResponse(
                "signup.html", {"request": request, "message": "User already exists"}, status_code=400
            )

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password)
        try:
            new_user.save()
            return templates.TemplateResponse(
                "signin.html", {"request": request, "message": "User created successfully"}, status_code=201
            )
        except Exception as error:
            return templates.TemplateResponse(
                "signup.html", {"request": request, "message": f"Failed to create user: {error}"}, status_code=409
            )

    # sign in
    async def signInUser(self, request: Request, *, email: str, password: str, recaptcha: str | None):
        # Recaptcha presence check
        if not recaptcha:
            return templates.TemplateResponse(
                "signin.html", {"request": request, "message": "Please select captcha"}, status_code=404
            )

        try:
            existing_user = User.objects(email=email).first()
            if not existing_user:
                return templates.TemplateResponse(
                    "signin.html", {"request": request, "message": "User doesn't exist"}, status_code=404
                )

            is_password_correct = False
            try:
                is_password_correct = bcrypt.checkpw(
                    password.encode("utf-8"), existing_user.password.encode("utf-8")
                )
            except Exception:
                is_password_correct = False

            if not is_password_correct:
                return templates.TemplateResponse(
                    "signin.html",
                    {"request": request, "message": "Invalid credentials || Incorrect Password"},
                    status_code=400,
                )

            request.session["user_email"] = email
            return RedirectResponse(url="/user/homepage", status_code=302)
        except Exception as error:
            return templates.TemplateResponse(
                "signin.html", {"request": request, "message": str(error)}, status_code=500
            )

    # forgot password
    async def forgotPassword(self, request: Request, *, email: str):
        try:
            existing_user = User.objects(email=email).first()
            if not existing_user:
                return templates.TemplateResponse(
                    "forgot-password.html", {"request": request, "message": "User doesn't exist"}, status_code=404
                )

            # Generate random password
            import secrets

            new_password = secrets.token_urlsafe(8)  # roughly 8 chars, URL safe
            hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            try:
                await transporter.sendMail(
                    to=email,
                    subject="Password Reset",
                    text=f"Your new password is: {new_password}",
                )
            except Exception as send_err:
                return templates.TemplateResponse(
                    "forgot-password.html",
                    {"request": request, "message": f"Not valid Email: {send_err}"},
                    status_code=404,
                )

            existing_user.password = hashed_password
            existing_user.save()

            return templates.TemplateResponse(
                "signin.html", {"request": request, "message": "New Password sent to your email"}, status_code=201
            )
        except Exception as error:
            return templates.TemplateResponse(
                "forgot-password.html", {"request": request, "message": str(error)}, status_code=500
            )

    # change password
    async def changePassword(self, request: Request, *, oldPassword: str, newPassword: str):
        try:
            email = request.session.get("user_email")
            if not email:
                return templates.TemplateResponse(
                    "change-password.html",
                    {"request": request, "message": "User doesn't exist"},
                    status_code=404,
                )

            existing_user = User.objects(email=email).first()
            if not existing_user:
                return templates.TemplateResponse(
                    "change-password.html", {"request": request, "message": "User doesn't exist"}, status_code=404
                )

            is_password_correct = False
            try:
                is_password_correct = bcrypt.checkpw(
                    oldPassword.encode("utf-8"), existing_user.password.encode("utf-8")
                )
            except Exception:
                is_password_correct = False

            if not is_password_correct:
                return templates.TemplateResponse(
                    "change-password.html", {"request": request, "message": "Invalid credentials"}, status_code=400
                )

            hashed_password = bcrypt.hashpw(newPassword.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            existing_user.password = hashed_password
            existing_user.save()
            return templates.TemplateResponse(
                "signin.html", {"request": request, "message": "Password changed successfully"}, status_code=201
            )
        except Exception as error:
            return templates.TemplateResponse(
                "change-password.html", {"request": request, "message": str(error)}, status_code=500
            )
