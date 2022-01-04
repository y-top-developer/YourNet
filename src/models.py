import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine, create_engine

from messages import generate_password

Base = declarative_base()
engine = create_engine('sqlite:///db.db?check_same_thread=False')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, nullable=False)
    mail = Column(String, default='', nullable=False)
    name = Column(String, default='', nullable=False)
    link = Column(String, default='', nullable=False)
    work = Column(String, default='', nullable=False)
    about = Column(String, default='', nullable=False)
    password = Column(String, default=generate_password(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return (f'{self.name}\n'
                f'*Профиль:* {self.link}\n\n'
                f'*Чем занимается:* {self.work}\n'
                f'*Зацепки для начала разговора:* {self.about}\n\n'
                f'Напиши собеседнику в Telegram – [{self.name}](tg://user?id={self.telegram_id})')


class Pair(Base):
    __tablename__ = 'pair'

    id = Column(Integer, primary_key=True)
    user_a = Column(String, nullable=False)
    user_b = Column(String, nullable=False)
    about = Column(String, default='', nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<Pair {self.id}; User A {self.user_a} - User B {self.user_b}>'


Base.metadata.create_all(engine)
