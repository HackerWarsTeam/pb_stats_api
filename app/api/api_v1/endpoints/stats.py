import re
from io import BytesIO
from typing import Any, List

import pytesseract
import requests
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, crud
from app.api import deps
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[schemas.Stats])
async def read_stats(
        *,
        db: AsyncSession = Depends(deps.async_get_db),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    Retrieve stats.
    """
    stats = await crud.stats.get_multi(db, skip=skip, limit=limit)
    if not stats:
        raise HTTPException(status_code=404, detail="No user was found")
    return stats


@router.get("/{user_vk_id}", response_model=schemas.Stats)
async def read_stats(
        *,
        db: AsyncSession = Depends(deps.async_get_db),
        user_vk_id: int,
) -> Any:
    """
    Retrieve stats by user_vk_id.
    """
    stats = await crud.stats.get_by_vk_id(db, user_vk_id=user_vk_id)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats


@router.post("/", response_model=schemas.Stats)
async def add_stats(
        *,
        db: AsyncSession = Depends(deps.async_get_db),
        stats_in: schemas.StatsCreate,
) -> Any:
    """
    Add new stats.
    """
    if (not stats_in.img_url and not stats_in.stats) or not stats_in.user_name:
        raise HTTPException(status_code=422, detail=f"Validation error")
    stats = await crud.stats.get_by_vk_id(db, user_vk_id=stats_in.user_vk_id)
    if not stats_in.img_url:
        if not stats:
            stats = await crud.stats.create(db, obj_in=stats_in)
        else:
            stats = await crud.stats.update(db, db_obj=stats, obj_in=stats_in)
        return stats
    response = requests.get(stats_in.img_url)
    img = Image.open(BytesIO(response.content))
    string = pytesseract.image_to_string(img, lang='rus')
    if stats_in.user_name not in string:
        string = pytesseract.image_to_string(img)
    if stats_in.user_name in string:
        try:
            stats_in.stats = string.split(stats_in.user_name, 1)[1]
            match = re.search('(\d+)', stats_in.stats)
            stats_in.stats = int(match.group(1))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to process a screenshot. Error: {e}. String: {string}")
    if not stats_in.stats:
        raise HTTPException(status_code=500, detail="User not found in the screenshot")
    if not stats:
        stats = await crud.stats.create(db, obj_in=stats_in)
    elif stats.stats < stats_in.stats:
        stats = await crud.stats.update(db, db_obj=stats, obj_in=stats_in)
    return stats


@router.post("/stats_from_api", response_model=schemas.Stats)
async def add_stats_from_api(
        *,
        db: AsyncSession = Depends(deps.async_get_db),
        stats_in: schemas.StatsCreate,
) -> Any:
    """
    Add new stats from api.
    """
    stats = await crud.stats.get_by_vk_id(db, user_vk_id=stats_in.user_vk_id)
    headers = {'x-vk-sign': settings.PIXELBATTLE_TOKEN,
               'content-type': 'application/json'}
    user_stats_from_api = requests.post('https://pixel-dev.w84.vkforms.ru/api/my',
                                        json={'friendIds': [stats_in.user_vk_id]},
                                        headers=headers)
    friends = user_stats_from_api.json()["response"]["friends"]
    for friend in friends:
        if friend.get("id") == stats_in.user_vk_id:
            stats_in.stats = friend.get("score", 0)
    if not stats_in.stats:
        raise HTTPException(status_code=404, detail="User not found")
    if not stats:
        stats = await crud.stats.create(db, obj_in=stats_in)
    elif stats.stats < stats_in.stats:
        stats = await crud.stats.update(db, db_obj=stats, obj_in=stats_in)
    return stats
