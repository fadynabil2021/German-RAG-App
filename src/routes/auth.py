from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from domains.shared.dependencies import get_db, get_user_repo
from domains.identity.repository import UserRepository
from domains.identity.service import IdentityService
from routes.schemes.auth import UserRegister, UserLogin, Token, UserResponse
from security.authentication import get_current_user
from models.db_schemes import User

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)

@auth_router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserRegister,
    user_repo: UserRepository = Depends(get_user_repo)
):
    service = IdentityService(user_repo)
    return await service.register_user(user_in)

@auth_router.post("/login", response_model=Token)
async def login(
    login_in: UserLogin,
    user_repo: UserRepository = Depends(get_user_repo)
):
    service = IdentityService(user_repo)
    user = await service.authenticate_user(login_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return service.generate_token(user)

@auth_router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
