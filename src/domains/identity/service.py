from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from security.authentication import verify_password, get_password_hash, create_access_token
from domains.identity.repository import UserRepository
from models.db_schemes import User
from routes.schemes.auth import UserRegister, UserLogin, Token, UserResponse

class IdentityService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: UserRegister) -> User:
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            password_hash=hashed_password,
            proficiency_level=user_in.proficiency_level,
            role="user"
        )
        return await self.user_repo.save(new_user)

    async def authenticate_user(self, login_in: UserLogin) -> Optional[User]:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.password_hash):
            return None
        return user

    def generate_token(self, user: User) -> Token:
        access_token = create_access_token(data={"sub": user.email})
        return Token(access_token=access_token, token_type="bearer")
