import re
import string
import secrets

from settings import COMPANY

re_mail = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
alphabet = string.ascii_letters + string.digits


def is_correct_mail(mail):
    return re_mail.fullmatch(mail) and mail.endswith(f'@{COMPANY}')


def generate_password():
    return ''.join(secrets.choice(alphabet) for i in range(20))