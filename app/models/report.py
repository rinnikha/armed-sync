from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Report(Base):
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)  # 'completed', 'processing', 'failed'
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")