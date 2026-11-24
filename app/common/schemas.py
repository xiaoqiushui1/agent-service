from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# 定义一个通用 泛型
T = TypeVar("T")


class PageResult(BaseSchema, Generic[T]):
    """通用分页结果"""

    items: list[T]
    page: int
    page_size: int
    total: int