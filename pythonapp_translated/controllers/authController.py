import os
from fastapi import Request
from fastapi.templating import Jinja2Templates

from models.userModel import User

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "views")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class googleSignInController:
    async def signInSuccess(self, request: Request):
        # Extract user data from session (set during OAuth callback)
        user_data = request.session.get("oauth_user")
        if not user_data:
            return templates.TemplateResponse(
                "signin.html",
                {"request": request, "message": "Not Authorized"},
                status_code=403,
            )

        email = user_data.get("email")
        name = user_data.get("name") or user_data.get("given_name") or "User"
        sub = user_data.get("sub") or user_data.get("id") or ""

        if email:
            user = User.objects(email=email).first()
            if user:
                request.session["user_email"] = email
                return templates.TemplateResponse("homepage.html", {"request": request}, status_code=200)

            new_user = User(username=name, email=email, password=sub)
            new_user.save()
            request.session["user_email"] = email
            return templates.TemplateResponse("homepage.html", {"request": request}, status_code=200)

        # If email is not present
        return templates.TemplateResponse(
            "signin.html", {"request": request, "message": "Not Authorized"}, status_code=403
        )

    def signInFailed(self, request: Request):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=401, content={"error": True, "message": "Log in failure"})
