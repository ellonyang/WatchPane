import datetime

from pydantic import BaseModel, ConfigDict


class WatchCreateSchema(BaseModel):
    name: str
    url: str


class WatchSchema(BaseModel):
    # 通过sqlalchemy的orm模型生成的表结构
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    url: str
    status: str
    last_check_at: str | None
    last_success_at: str | None
    last_execute_at: str | None
    failed_count: int


class WatchUpdateSchema(BaseModel):
    id: int
    status: str
    last_check_at: str | datetime.datetime | None
    last_success_at: str | datetime.datetime | None
    last_executed_at: str | datetime.datetime | None
    failed_count: int
