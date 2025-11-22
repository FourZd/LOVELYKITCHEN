from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.database import BaseModel


class Organization(BaseModel):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    members: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    deals: Mapped[list["Deal"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


from users.models import OrganizationMember
from contacts.models import Contact
from deals.models import Deal

