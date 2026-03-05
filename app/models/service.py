import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class Service(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint(
            "status != 'deprecated' OR deprecated_at IS NOT NULL",
            name="ck_service_deprecated_at_set",
        ),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ServiceStatus] = mapped_column(
        Enum(ServiceStatus, name="servicestatus"),
        nullable=False,
        default=ServiceStatus.ACTIVE,
    )
    team_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    deprecated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    team: Mapped["Team"] = relationship(  # noqa: F821
        "Team", back_populates="service"
    )
