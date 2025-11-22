from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.database import BaseModel
from activities.enums import ActivityType


class Activity(BaseModel):
    __tablename__ = "activities"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    deal_id: Mapped[UUID] = mapped_column(ForeignKey("deals.id"), nullable=False)
    author_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    type: Mapped[ActivityType] = mapped_column(Enum(ActivityType), nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    deal: Mapped["Deal"] = relationship(back_populates="activities")
    author: Mapped[Optional["User"]] = relationship(back_populates="authored_activities")


from deals.models import Deal
from users.models import User

