from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PriceList(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    min_quantity = Column(Integer, default=1)
    template_id = Column(Integer, nullable=True)  # Could be linked to a templates table
    additional_settings = Column(JSON, nullable=True)
    pdf_path = Column(String, nullable=True)
    last_generated_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    created_by = relationship("User")