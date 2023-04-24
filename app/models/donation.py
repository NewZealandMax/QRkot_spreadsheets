from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.db import Base
from app.models.base import CharityBase


class Donation(CharityBase, Base):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
