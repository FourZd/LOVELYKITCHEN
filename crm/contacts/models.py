from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.database import BaseModel


class Contact(BaseModel):
    __tablename__ = "contacts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    organization: Mapped["Organization"] = relationship(back_populates="contacts")
    owner: Mapped["User"] = relationship(back_populates="owned_contacts")
    deals: Mapped[list["Deal"]] = relationship(back_populates="contact")


from organizations.models import Organization
from users.models import User
from deals.models import Deal

