from fastapi import Depends, HTTPException, status
from security.authentication import get_current_user
from models.db_schemes import User, Message
from domains.shared.dependencies import get_db, get_message_repo, get_asset_repo
from domains.learning.asset_repository import AssetRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date
from helpers.config import get_settings, Settings

settings = get_settings()

async def check_message_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ensures the user hasn't exceeded their daily RAG message quota.
    """
    if current_user.role == 'admin' or current_user.tier == 'pro':
        return True

    # Count messages sent by this user TODAY
    today = date.today()
    query = select(func.count(Message.message_id)).join(Message.conversation).where(
        Message.role == 'user',
        Message.created_at >= today,
        Message.conversation.has(user_id=current_user.user_id)
    )
    
    result = await db.execute(query)
    count = result.scalar() or 0
    
    if count >= settings.FREE_TIER_DAILY_MESSAGE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Daily quota of {settings.FREE_TIER_DAILY_MESSAGE_LIMIT} messages reached. Upgrade for more!"
        )
    
    return True

async def check_asset_quota(
    current_user: User = Depends(get_current_user),
    asset_repo: AssetRepository = Depends(get_asset_repo),
    settings: Settings = Depends(get_settings)
):
    """
    Ensures the user hasn't exceeded their asset storage quota.
    """
    if current_user.role == 'admin' or current_user.tier == 'pro':
        return True
    
    count = await asset_repo.get_count_by_owner(current_user.user_id)
    if count >= settings.FREE_TIER_MAX_ASSETS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Storage limit reached ({settings.FREE_TIER_MAX_ASSETS} assets). Upgrade to Pro for unlimited storage!"
        )
    return True
