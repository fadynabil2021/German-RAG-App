from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from domains.shared.repository import BaseRepository
from models.db_schemes.minirag.schemes.conversation import Conversation, Message

class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .filter(Conversation.conversation_id == id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalars().first()

    async def get_by_project(self, project_id: int) -> List[Conversation]:
        result = await self.session.execute(
            select(Conversation).filter(Conversation.project_id == project_id)
        )
        return list(result.scalars().all())

    async def save(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def delete(self, id: int) -> bool:
        conversation = await self.get_by_id(id)
        if conversation:
            await self.session.delete(conversation)
            return True
        return False

    async def list(self, skip: int = 0, limit: int = 100) -> List[Conversation]:
        result = await self.session.execute(
            select(Conversation).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_by_conversation(self, conversation_id: int) -> List[Message]:
        result = await self.session.execute(
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
