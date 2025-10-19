from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, server_default="pending")
    stripe_session_id = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    
    # Relaciones
    user = relationship("User", back_populates="payments")