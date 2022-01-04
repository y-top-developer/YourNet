import logging
from re import L
from sqlalchemy.orm import sessionmaker

from models import User, Pair, engine

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

session = sessionmaker(engine)()


def get_user(user_id):
    user = (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .first()
    )
    return user if user else None


def create_user(user_id):
    if not get_user(user_id):
        session.add(User(
            telegram_id=user_id
        ))
        session.commit()


def set_field(user_id, key, value):
    (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .update(
            {key: value}
        )
    )
    session.commit()
