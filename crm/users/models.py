from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, func, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.database import BaseModel
from users.enums import UserRole


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(300), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    organization_memberships: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    owned_contacts: Mapped[list["Contact"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    owned_deals: Mapped[list["Deal"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    authored_activities: Mapped[list["Activity"]] = relationship(
        back_populates="author"
    )


class OrganizationMember(BaseModel):
    __tablename__ = "organization_members"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_user"),
    )

    organization: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="organization_memberships")


from organizations.models import Organization
from contacts.models import Contact
from deals.models import Deal
from activities.models import Activity

