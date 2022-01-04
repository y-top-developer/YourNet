from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()
engine = create_engine('sqlite:///db.db?check_same_thread=False')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, nullable=False)
    name = Column(String, default='', nullable=False)
    mail = Column(String, default='', nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    password = Column(String, nullable=False)
    link = Column(String, default='', nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<User @{self.id}>'


class Pair(Base):
    __tablename__ = 'pair'

    id = Column(Integer, primary_key=True)
    user_a = Column(String, nullable=False)
    user_b = Column(String, nullable=False)
    was_success = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<Pair @{self.id}; User A @{self.user_a} - User B @{self.user_b}>'


Base.metadata.create_all(engine)
