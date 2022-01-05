import logging
from re import L
from sqlalchemy.orm import sessionmaker

from models import User, Pair, engine
from messages import generate_password

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


def get_admins():
    admins = (
        session.query(
            User
        )
        .filter(
            User.is_admin == True,
        )
        .all()
    )
    return admins if admins else []


def get_users():
    users = (
        session.query(
            User
        )
        .all()
    )
    return users if users else []


def get_active_users():
    users = (
        session.query(
            User
        )
        .filter(
            User.is_active == True
        )
        .all()
    )
    return users if users else []


def create_user(user_id):
    if not get_user(user_id):
        session.add(User(
            telegram_id=user_id,
            password=generate_password(),
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


def create_pair(user_id_a, user_id_b):
    session.add(Pair(
        user_a=user_id_a,
        user_b=user_id_b,
    ))
    session.commit()


def delete_pairs():
    session.query(Pair).delete()


def get_pairs():
    pairs = (
        session.query(
            Pair
        )
        .all()
    )
    return pairs if pairs else []
