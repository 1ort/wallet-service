import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DECIMAL, UUID, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, User


class TransactionType(enum.Enum):
    WITHDRAW = enum.auto()
    DEPOSIT = enum.auto()


class Transaction(Base):
    __tablename__ = "transaction"

    uid: Mapped[UUID] = mapped_column(UUID(True), primary_key=True, index=True)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(16, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="transactions")
