import datetime

from pydantic import BaseModel
from typing import Optional


# Shared properties
class StatsBase(BaseModel):
    user_vk_id: int
    img_url: Optional[str]


# Properties to receive via API on creation
class StatsCreate(StatsBase):
    user_name: Optional[str] = None
    stats: Optional[int] = None


# Properties to receive via API on update
class StatsUpdate(StatsBase):
    user_name: Optional[str] = None
    stats: Optional[int] = None


class StatsInDBBase(StatsBase):
    stats: int
    create_date: datetime.datetime
    update_date: datetime.datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class Stats(StatsInDBBase):
    pass


# Additional properties stored in DB
class StatsInDB(StatsInDBBase):
    pass

