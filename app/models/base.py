from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def as_dict(self) -> dict[str, str]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
