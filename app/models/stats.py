from sqlalchemy import Column, Integer, String, DateTime

from app.db.base_class import Base


class Stats(Base):
    user_vk_id = Column(Integer, primary_key=True, index=True)
    stats = Column(Integer, nullable=False)
    img_url = Column(String(500))
    create_date = Column(DateTime, nullable=False)
    update_date = Column(DateTime, nullable=False)
