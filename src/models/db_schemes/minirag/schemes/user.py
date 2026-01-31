from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(SQLAlchemyBase):

    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="user", nullable=False)
    proficiency_level = Column(String(10), default="A1", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    projects = relationship("Project", back_populates="user")
