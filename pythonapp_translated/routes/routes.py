from typing import Optional
from fastapi import APIRouter, Request, Form

from controllers.controller import UserGetController, UserPostController

router = APIRouter()

UserGetControllerInstance = UserGetController()
UserPostControllerInstance = UserPostController()


# GET REQUESTS
@router.get("/signup")
def get_signup(request: Request):
    return UserGetControllerInstance.getSignUpPage(request)


@router.get("/signin")
def get_signin(request: Request):
    return UserGetControllerInstance.getSignInPage(request)


@router.get("/homepage")
def get_homepage(request: Request):
    return UserGetControllerInstance.homePage(request)


@router.get("/signout")
def signout(request: Request):
    return UserGetControllerInstance.logoutUser(request)


@router.get("/forgot-password")
def get_forgot_password(request: Request):
    return UserGetControllerInstance.getForgotPassword(request)


@router.get("/change-password")
def get_change_password(request: Request):
    return UserGetControllerInstance.getChangePassword(request)


# POST REQUESTS
@router.post("/signup")
async def post_signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    cpassword: str = Form(...),
):
    return await UserPostControllerInstance.createUser(
        request, username=username, email=email, password=password, cpassword=cpassword
    )


@router.post("/signin")
async def post_signin(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    g_recaptcha_response: Optional[str] = Form(None, alias="g-recaptcha-response"),
):
    return await UserPostControllerInstance.signInUser(
        request, email=email, password=password, recaptcha=g_recaptcha_response
    )


@router.post("/forgot-password")
async def post_forgot_password(request: Request, email: str = Form(...)):
    return await UserPostControllerInstance.forgotPassword(request, email=email)


@router.post("/change-password")
async def post_change_password(
    request: Request,
    oldPassword: str = Form(...),
    newPassword: str = Form(...),
):
    return await UserPostControllerInstance.changePassword(
        request, oldPassword=oldPassword, newPassword=newPassword
    )
