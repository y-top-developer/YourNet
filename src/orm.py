from models import User, Pair
from messages import generate_password


def get_user(session, user_id):
    return (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .first()
    )


def get_password(session, user_id):
    return (
        session.query(
            User.password
        )
        .filter(
            User.telegram_id == user_id,
        )
        .first()
    )


def is_active(session, user_id):
    return (
        session.query(
            User.is_active
        )
        .filter(
            User.telegram_id == user_id,
        )
        .first()
    ) == (True,)


def set_active(session, user_id, mode):
    (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .update(
            {'is_active': mode}
        )
    )
    session.commit()


def register_user(session, user_id):
    if not get_user(session, user_id):
        session.add(User(
            telegram_id=user_id,
            password=generate_password(),
        ))
        session.commit()


def set_link(session, user_id, link):
    (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .update(
            {'link': link}
        )
    )
    session.commit()


def set_admin(session, user_id, mode):
    (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .update(
            {'is_admin': mode}
        )
    )
    session.commit()


def set_mail(session, user_id, mail):
    (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .update(
            {'mail': mail}
        )
    )
    session.commit()


def set_verified(session, user_id):
    (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .update(
            {'is_verified': True}
        )
    )
    session.commit()


def set_name(session, user_id, name):
    (
        session.query(
            User
        )
        .filter(
            User.telegram_id == user_id,
        )
        .update(
            {'name': name}
        )
    )
    session.commit()


def is_verified(session, user_id):
    return (
        session.query(
            User.is_verified
        )
        .filter(
            User.telegram_id == user_id,
        )
        .first()
    ) == (True,)


def is_admin(session, user_id):
    return (
        session.query(
            User.is_admin
        )
        .filter(
            User.telegram_id == user_id,
        )
        .first()
    ) == (True,)


def get_profile(session, user_id):
    return (
        session.query(
            User.name,
            User.mail,
            User.link,
        )
        .filter(
            User.telegram_id == user_id,
        )
        .first()
    )

def get_users(session):
    return (
        session.query(
            User.name,
            User.mail,
            User.link,
            User.password,
        )
        .all()
    )