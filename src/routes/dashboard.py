from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from domains.shared.dependencies import get_db
from security.authentication import get_current_user
from models.db_schemes import User, Message, Project
import logging

logger = logging.getLogger(__name__)

dashboard_router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
)

@dashboard_router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user-scoped dashboard statistics.
    Returns real data from DB, or explicit zeros if no data.
    """
    user_id = current_user.user_id
    
    # Words learned (approximated from unique message count * avg words)
    try:
        message_count_result = await db.execute(
            select(func.count(Message.message_id))
            .join(Project, Message.conversation_id == Project.project_id)
            .where(Project.owner_id == user_id)
        )
        message_count = message_count_result.scalar() or 0
        words_learned = message_count * 15  # Approximation: 15 words per interaction
    except Exception as e:
        logger.warning(f"Failed to count messages: {e}")
        message_count = 0
        words_learned = 0
    
    # Total sessions (count of distinct days with activity)
    try:
        sessions_result = await db.execute(
            select(func.count(func.distinct(func.date(Message.created_at))))
            .join(Project, Message.conversation_id == Project.project_id)
            .where(Project.owner_id == user_id)
        )
        total_sessions = sessions_result.scalar() or 0
    except Exception:
        total_sessions = 0
    
    # Total time (approximation: 3 minutes per message)
    total_time_minutes = message_count * 3
    
    # Streak calculation (consecutive days with activity)
    streak_days = 0
    try:
        # Get distinct activity dates, ordered descending
        dates_result = await db.execute(
            select(func.distinct(func.date(Message.created_at)))
            .join(Project, Message.conversation_id == Project.project_id)
            .where(Project.owner_id == user_id)
            .order_by(func.date(Message.created_at).desc())
        )
        dates = [row[0] for row in dates_result.fetchall()]
        
        if dates:
            today = datetime.now().date()
            if dates[0] == today or dates[0] == today - timedelta(days=1):
                streak_days = 1
                for i in range(1, len(dates)):
                    if dates[i] == dates[i-1] - timedelta(days=1):
                        streak_days += 1
                    else:
                        break
    except Exception:
        streak_days = 0
    
    # Project count
    try:
        project_count_result = await db.execute(
            select(func.count(Project.project_id))
            .where(Project.owner_id == user_id)
        )
        project_count = project_count_result.scalar() or 0
    except Exception:
        project_count = 0
    
    return {
        "words_learned": words_learned,
        "total_sessions": total_sessions,
        "total_time_minutes": total_time_minutes,
        "streak_days": streak_days,
        "project_count": project_count,
        "message_count": message_count,
    }
