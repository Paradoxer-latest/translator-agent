# routes/user.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.controller import UserGetController, UserPostController

router = APIRouter()

# Controller instances
user_get_controller = UserGetController()
user_post_controller = UserPostController()

# GET routes
@router.get("/signup")
async def get_signup_page(request: Request, db: Session = Depends(get_db)):
    return await user_get_controller.getSignUpPage(request, db)


@router.get("/signin")
async def get_signin_page(request: Request, db: Session = Depends(get_db)):
    return await user_get_controller.getSignInPage(request, db)


@router.get("/homepage")
async def get_homepage(request: Request, db: Session = Depends(get_db)):
    return await user_get_controller.homePage(request, db)


@router.get("/signout")
async def signout(request: Request, db: Session = Depends(get_db)):
    return await user_get_controller.logoutUser(request, db)


@router.get("/forgot-password")
async def get_forgot_password(request: Request, db: Session = Depends(get_db)):
    return await user_get_controller.getForgotPassword(request, db)


@router.get("/change-password")
async def get_change_password(request: Request, db: Session = Depends(get_db)):
    return await user_get_controller.getChangePassword(request, db)


# POST routes
@router.post("/signup")
async def signup(request: Request, db: Session = Depends(get_db)):
    return await user_post_controller.createUser(request, db)


@router.post("/signin")
async def signin(request: Request, db: Session = Depends(get_db)):
    return await user_post_controller.signInUser(request, db)


@router.post("/forgot-password")
async def forgot_password(request: Request, db: Session = Depends(get_db)):
    return await user_post_controller.forgotPassword(request, db)


@router.post("/change-password")
async def change_password(request: Request, db: Session = Depends(get_db)):
    return await user_post_controller.changePassword(request, db)