from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, func
from sqlalchemy.orm import relationship

class LearningPath(SQLAlchemyBase):
    __tablename__ = "learning_paths"

    path_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    target_level = Column(String(10), nullable=False) # e.g., 'B1'
    status = Column(String(50), default="active") # active, completed, paused
    
    goals = Column(JSON, nullable=True) # List of specific goals
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User")

class Progress(SQLAlchemyBase):
    __tablename__ = "progress"

    progress_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    topic = Column(String(255), nullable=False)
    mastery_score = Column(Float, default=0.0) # 0.0 to 1.0
    
    last_reviewed = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    next_review = Column(DateTime(timezone=True), nullable=True)
    
    # Links to documents/assets that contributed to this progress
    metadata_info = Column(JSON, nullable=True)

    user = relationship("User")
