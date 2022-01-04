import logging

from sqlalchemy.sql.functions import user
import telebot
from telebot import types, custom_filters
from sqlalchemy.orm import sessionmaker

from models import engine
from settings import ADMINS, TELEGRAM_TOKEN
from orm import get_password, set_active, register_user, set_link, set_admin, set_mail, is_verified, set_verified, get_profile, is_active, is_admin, set_name, get_users
from messages import send_password, is_correct_mail, is_correct_company

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

session = sessionmaker(engine)()
bot = telebot.TeleBot(TELEGRAM_TOKEN)


class States:
    send_mail = 1
    ask_password = 2
    ask_name = 3
    ask_about = 4
    ask_mode = 5


def ask_about_mode(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 2

    button_run = types.InlineKeyboardButton(text='Я в деле!🔥', callback_data='run')
    button_stop = types.InlineKeyboardButton(text='В другой раз😴', callback_data='stop')

    keyboard.add(button_run, button_stop)

    bot.send_message(chat_id, 'Участвуешь на этой неделе?', reply_markup=keyboard)


def help(chat_id):
    if is_verified(session, chat_id):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row_width = 2

        button_profile = types.InlineKeyboardButton(text='Мой профиль', callback_data='my_profile')
        button_mode = types.InlineKeyboardButton(text='Мой статус', callback_data='my_mode')
        button_change = types.InlineKeyboardButton(text='Поменять статус', callback_data='change_mode')

        keyboard.add(button_profile, button_mode)
        keyboard.add(button_change)

        if is_admin(session, chat_id):
            button_users = types.InlineKeyboardButton(text='Участники', callback_data='get_users')
            button_pairs = types.InlineKeyboardButton(text='Пары', callback_data='get_pairs')
            keyboard.add(button_users, button_pairs)

            button_generate_pairs = types.InlineKeyboardButton(
                text='Сгенерировать пары', callback_data='generate_pairs')
            button_send_invites = types.InlineKeyboardButton(text='Отправить приглашения', callback_data='send_invites')
            keyboard.add(button_generate_pairs, button_send_invites)

        bot.send_message(chat_id, 'Настройки', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help_handler(message):
    help(message.from_user.id)


@bot.message_handler(commands=['start'])
def start(message):
    register_user(session, message.from_user.id)
    if message.from_user.username in ADMINS:
        set_admin(session, message.from_user.id, True)
    if is_verified(session, message.from_user.id):
        bot.set_state(message.from_user.id, States.ask_name)
        bot.send_message(message.from_user.id,
                         'Привет, рад тебя видеть!🤩\nКак тебы зовут?')
    else:
        bot.set_state(message.from_user.id, States.send_mail)
        bot.send_message(message.from_user.id,
                         'Привет, рад тебя видеть!🤩\nВведи свой корпоративный mail, чтобы получить пароль📧')


@bot.message_handler(state=States.send_mail)
def send_password_telegram(message):
    mail = message.text
    user_id = message.from_user.id
    if is_correct_mail(mail) and is_correct_company(mail):
        set_mail(session, user_id, mail)
        send_password(mail, get_password(session, user_id))
        bot.send_message(user_id, 'Отправил📮\nВведи пароль из письма🔑')
        bot.set_state(user_id, States.ask_password)
    elif not is_correct_mail(mail):
        bot.send_message(user_id, 'Что-то с форматом⚠️')
    elif not is_correct_company(mail):
        bot.send_message(user_id, 'Не знаю такой компании⚠️')
    else:
        bot.send_message(user_id, 'Что-то не так😔')


@bot.message_handler(state=States.ask_password)
def ask_info(message):
    password = message.text
    user_id = message.from_user.id
    if get_password(session, user_id) == (password,):
        set_verified(session, user_id)
        bot.send_message(user_id,
                         'Ты в системе🌐\n\nКак тебя зовут?')
        bot.set_state(message.from_user.id, States.ask_name)
    else:
        bot.send_message(user_id, 'Пароль не подходит⚠️')


@bot.message_handler(state=States.ask_name)
def done(message):
    name = message.text
    set_name(session, message.from_user.id, name)
    bot.send_message(message.from_user.id,
                     'Рад познакомиться!)\n\nПришли ссылку на свой профиль в любой социальной сети. Так вы в паре сможете лучше узнать друг о друге до встречи🔎')
    bot.set_state(message.from_user.id, States.ask_mode)
    ask_about_mode(message.from_user.id)


@bot.message_handler(state=States.ask_about)
def done(message):
    link = message.text
    set_link(session, message.from_user.id, link)
    set_active(session, message.from_user.id, True)
    bot.send_message(message.from_user.id, 'Отлично, все готово!✨\nСвою пару для встречи ты будешь узнавать каждый понедельник — сообщение придет в этот чат\n\nНапиши партнеру в Telegram, чтобы договориться о встрече или звонке\nВремя и место вы выбираете сами')
    bot.set_state(message.from_user.id, States.ask_mode)
    ask_about_mode(message.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == 'run')
def run_callback(call):
    set_active(session, call.from_user.id, True)
    bot.answer_callback_query(call.id, 'Жди пару!)')


@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_callback(call):
    set_active(session, call.from_user.id, False)
    bot.answer_callback_query(call.id, 'Заходи еще!)')


@bot.callback_query_handler(func=lambda call: call.data == 'my_profile')
def my_profile_callback(call):
    profile = get_profile(session, call.from_user.id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, f'🕴️{profile[0]}\n📧 {profile[1]}\n🤳 {profile[2]}')


@bot.callback_query_handler(func=lambda call: call.data == 'my_mode')
def my_mode_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, 'Ты в деле!' if is_active(session, call.from_user.id) else 'На паузе')


@bot.callback_query_handler(func=lambda call: call.data == 'change_mode')
def change_mode_callback(call):
    bot.answer_callback_query(call.id)
    ask_about_mode(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == 'get_users')
def get_users_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, '\n'.join([
        f'\'{user[0]}\' - \'{user[1]}\' - is_active? {user[2]} - \'{user[3]}\' - \'{user[4]}\'' for user in get_users(session)
    ]))


@bot.callback_query_handler(func=lambda call: call.data == 'get_pairs')
def get_pairs_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, 'Генерирую пары')


@ bot.callback_query_handler(func=lambda call: call.data == 'generate_pairs')
def change_mode_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, 'Отправил приглашения')


@ bot.callback_query_handler(func=lambda call: call.data == 'send_invites')
def change_mode_callback(call):
    bot.answer_callback_query(call.id)
    ask_about_mode(call.from_user.id)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

if __name__ == "__main__":
    bot.polling()
