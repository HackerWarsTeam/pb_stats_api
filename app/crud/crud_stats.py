import datetime
from typing import Any, Dict, Optional, Union

from sqlalchemy.sql.expression import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.stats import Stats
from app.schemas.stats import StatsCreate, StatsUpdate


class CRUDStats(CRUDBase[Stats, StatsCreate, StatsUpdate]):
    async def get_by_vk_id(self, db: AsyncSession, *, user_vk_id: int) -> Optional[Stats]:
        results = await db.execute(select(Stats).filter(Stats.user_vk_id == user_vk_id))
        return results.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: StatsCreate) -> Stats:
        db_obj = Stats(
            user_vk_id=obj_in.user_vk_id,
            stats=obj_in.stats,
            img_url=obj_in.img_url,
            create_date=datetime.datetime.now(),
            update_date=datetime.datetime.now()
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


stats = CRUDStats(Stats)
