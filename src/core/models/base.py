from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr
from src.core.config import DBConfigurer
from src.core.settings import settings


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.NAMING_CONVENTION
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return DBConfigurer.utils.camel2snake(cls.__name__)
