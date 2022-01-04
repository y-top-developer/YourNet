import re
import string
import random
import secrets

from settings import COMPANY

re_mail = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
alphabet = string.ascii_letters + string.digits


def send_password(mail, password):
    print(f'Отправил пароль {password}')


def is_correct_mail(mail):
    return re_mail.fullmatch(mail)


def generate_password():
    return ''.join(secrets.choice(alphabet) for i in range(16))


def is_correct_company(mail):
    return mail.endswith(f'@{COMPANY}')


def generate_pairs(session):
    from orm import get_active_users, set_pair, delete_pairs
    delete_pairs(session)
    all_active_users = get_active_users(session)
    random.shuffle(all_active_users)
    pairs = [all_active_users[i:i + 2] for i in range(0, len(all_active_users), 2)]
    for pair in pairs:
        if len(pair) == 2:
            set_pair(session, pair[0][0], pair[1][0])
