"""API Key model."""

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class APIKey(Base, TimestampMixin):
    """API Key model for authentication and authorization."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    prefix: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    plan: Mapped[str] = mapped_column(
        String(50), nullable=False, default="free", index=True
    )  # free, pro, enterprise
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_api_keys_prefix_revoked", "prefix", "revoked_at"),
        Index("idx_api_keys_owner_plan", "owner_email", "plan"),
    )

    def is_active(self) -> bool:
        """Check if the API key is active."""
        return self.revoked_at is None
