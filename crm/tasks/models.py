from datetime import datetime, date
from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, func, Boolean, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.database import BaseModel


class Task(BaseModel):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    deal_id: Mapped[UUID] = mapped_column(ForeignKey("deals.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    deal: Mapped["Deal"] = relationship(back_populates="tasks")


from deals.models import Deal

