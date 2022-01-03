from models import User, Company, Pair
from messages import generate_password, is_correct_mail


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


def set_active(session, user_id, mode):
    pass
