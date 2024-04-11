import datetime
import enum
from typing import Optional, Type

from sqlalchemy import create_engine, Enum, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.operators import or_

engine = create_engine("sqlite:///database.sqlite")


class Base(DeclarativeBase):
    __abstract__ = True


class StatusEnum(enum.Enum):
    uncheck = "UNCHECK"
    running = "RUNNING"
    failed = "FAILED"


class WatchModel(Base):
    __tablename__ = "watch"
    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str]
    status: Mapped[str] = mapped_column(Enum(StatusEnum), default=StatusEnum.uncheck)
    last_check_at: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)
    last_success_at: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)
    last_execute_at: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)
    # 连续失败次数
    failed_count: Mapped[int] = mapped_column(default=0)


Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


init_db()


class Curds:
    def __init__(self, model: Type[WatchModel]):
        self.model = model

    def add(self, name, url, session):
        watch = self.model(name=name, url=url)
        session.add(watch)
        session.commit()
        session.refresh(watch)
        return watch

    def update(self, watch_id, status, last_check_at, last_success_at, last_executed_at, failed_count, session):
        watch = session.get(self.model, watch_id)
        watch.status = status
        watch.last_check_at = last_check_at
        watch.last_success_at = last_success_at
        watch.last_executed_at = last_executed_at
        watch.failed_count = failed_count
        session.add(watch)
        session.commit()
        return watch

    def update_by_model(self, model, session):
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    def get_watch(self, watch_id, session):
        return session.scalar(
            select(self.model).filter(self.model.id == watch_id)
        )

    def get_by_name(self, name, session):
        return session.scalar(
            select(self.model).filter(self.model.name == name)
        )

    def filter_by_last_check_at(self, interval: int, session):
        return session.scalars(
            select(self.model).filter(
                or_(self.model.last_check_at.is_(None),
                    self.model.last_check_at < datetime.datetime.now() - datetime.timedelta(seconds=interval)
                    )
            )
        )

    def all(self, session):
        return session.scalars(
            select(self.model).order_by(
                self.model.last_success_at.desc()
            )
        )


curd = Curds(WatchModel)
