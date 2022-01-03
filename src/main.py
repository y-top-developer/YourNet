import logging
import telebot
from telebot import types, custom_filters
from sqlalchemy.orm import sessionmaker

from models import engine
from settings import TELEGRAM_TOKEN
from messages import send_password, is_correct_mail
from orm import get_password, set_active

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

session = sessionmaker(engine)()
bot = telebot.TeleBot(TELEGRAM_TOKEN)


class States:
    send_mail = 1
    ask_password = 2
    ask_about = 3
    ask_mode = 4
    is_admin = 5


def ask_about_mode(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 2

    button_run = types.InlineKeyboardButton(text='Я в деле!🔥', callback_data='run')
    button_stop = types.InlineKeyboardButton(text='В другой раз😴', callback_data='stop')

    keyboard.add(button_run, button_stop)

    bot.send_message(chat_id, 'Участвуешь на этой неделе?', reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def start(message):
    bot.set_state(message.from_user.id, States.send_mail)
    bot.send_message(message.from_user.id,
                     'Привет, рад тебя видеть!🤩\nВведи свой корпоративный mail, чтобы получить пароль📧')


@bot.message_handler(state=States.send_mail)
def send_password_telegram(message):
    mail = message.text
    user_id = message.from_user.id
    if is_correct_mail(mail):
        send_password(mail, get_password(session, user_id))
        bot.send_message(user_id, 'Отправил📮\nВведи пароль из письма🔑')
        bot.set_state(user_id, States.ask_password)
    elif not is_correct_mail(mail):
        bot.send_message(user_id, 'Что-то с форматом⚠️')
    else:
        bot.send_message(user_id, 'Что-то не так😔')


@bot.message_handler(state=States.ask_password)
def ask_info(message):
    user_id = message.from_user.id
    bot.send_message(user_id,
                     'Ты в системе🌐\n\nПришли ссылку на свой профиль в любой социальной сети. Так вы в паре сможете лучше узнать друг о друге до встречи🔎')
    bot.set_state(message.from_user.id, States.ask_about)


@bot.message_handler(state=States.ask_about)
def done(message):
    bot.send_message(message.from_user.id, 'Отлично, все готово!✨')
    bot.set_state(message.from_user.id, States.ask_mode)
    ask_about_mode(message.from_user.id)


@bot.message_handler(commands=['mode'])
def get_mode(message):
    ask_about_mode(message.from_user.id)


@bot.callback_query_handler(func=lambda call: True)
def get_mode_callback(call):
    if call.data == "run":
        set_active(session, call.from_user.id, True)
        bot.answer_callback_query(call.id, 'Жди пару!)')
    elif call.data == "stop":
        set_active(session, call.from_user.id, False)
        bot.answer_callback_query(call.id, 'Заходи еще!)')


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

if __name__ == "__main__":
    bot.polling()
