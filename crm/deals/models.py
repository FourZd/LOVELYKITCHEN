from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import String, DateTime, ForeignKey, func, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.database import BaseModel
from deals.enums import DealStatus, DealStage


class Deal(BaseModel):
    __tablename__ = "deals"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    contact_id: Mapped[UUID] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    status: Mapped[DealStatus] = mapped_column(Enum(DealStatus), nullable=False, default=DealStatus.NEW)
    stage: Mapped[DealStage] = mapped_column(Enum(DealStage), nullable=False, default=DealStage.QUALIFICATION)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    organization: Mapped["Organization"] = relationship(back_populates="deals")
    contact: Mapped["Contact"] = relationship(back_populates="deals")
    owner: Mapped["User"] = relationship(back_populates="owned_deals")
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
    activities: Mapped[list["Activity"]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )


from organizations.models import Organization
from contacts.models import Contact
from users.models import User
from tasks.models import Task
from activities.models import Activity

