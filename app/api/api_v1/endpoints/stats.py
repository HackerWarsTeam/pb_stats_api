from io import BytesIO
from typing import Any

import pytesseract
import requests
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, crud
from app.api import deps

router = APIRouter()


@router.get("/{user_vk_id}", response_model=schemas.Stats)
async def read_stats(
        *,
        db: AsyncSession = Depends(deps.async_get_db),
        user_vk_id: int,
) -> Any:
    """
    Retrieve stats.
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
    response = requests.get(stats_in.img_url)
    img = Image.open(BytesIO(response.content))
    string = pytesseract.image_to_string(img, lang='RUS')
    if stats_in.user_name not in string:
        string = pytesseract.image_to_string(img)
    if stats_in.user_name in string:
        try:
            stats_in.stats = int(string.split(stats_in.user_name, 1)[1].split("\n", 2)[1])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to process a screenshot. Error: {e}")
    if not stats_in.stats:
        raise HTTPException(status_code=500, detail="Unable to process a screenshot")
    stats = await crud.stats.get_by_vk_id(db, user_vk_id=stats_in.user_vk_id)
    if not stats:
        stats = await crud.stats.create(db, obj_in=stats_in)
    else:
        stats = await crud.stats.update(db, obj_in=stats_in)
    return stats
