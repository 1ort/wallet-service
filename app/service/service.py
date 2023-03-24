from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Transaction, TransactionType, User
from app.service import InsufficientFunds


class UserService:
    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self.session = session

    async def create_user(self, username: str) -> User:
        new_user = User(name=username)
        async with self.session() as conn:
            conn.add(new_user)
        return new_user

    async def get_user(self, user_id: int) -> User | None:
        query = select(User).filter(User.id == user_id).limit(1)
        async with self.session() as conn:
            result = await conn.execute(query)
            user = result.scalar()
            return user


class WalletService:
    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self.session = session

    async def execute_transaction(self, user: User, transaction: Transaction) -> None:
        assert user.id == transaction.user_id

        async with self.session() as conn:
            try:
                async with conn.begin():
                    user.balance += (
                        transaction.amount
                        if transaction.type is TransactionType.DEPOSIT
                        else -transaction.amount
                    )
                    conn.add_all(
                        [
                            user,
                            transaction,
                        ]
                    )
            except IntegrityError:
                raise InsufficientFunds

    async def calculate_balance(self, user: User, at_time: datetime) -> Decimal:
        query = select(Transaction).filter(
            Transaction.user_id == user.id and Transaction.timestamp > at_time
        )
        final_balance = user.balance
        async with self.session() as conn:
            result = await conn.execute(query)
            for transaction in result.scalars():
                final_balance += (
                    transaction.amount
                    if transaction.type is TransactionType.WITHDRAW
                    else -transaction.amount
                )
        return final_balance

    async def get_transaction(self, transaction_id: UUID) -> Transaction | None:
        query = select(Transaction).filter(Transaction.uid == transaction_id)
        async with self.session() as conn:
            result = await conn.execute(query)
            transaction = result.scalar()
            return transaction
