import random
import telebot
import schedule
from time import sleep
from threading import Thread
from telebot import types, custom_filters

from settings import ADMINS, TELEGRAM_TOKEN, SMTP
from messages import generate_password, is_correct_mail
from orm import get_user, set_field, create_user, get_admins, get_users, get_active_users, create_pair, delete_pairs, get_pairs

bot = telebot.TeleBot(TELEGRAM_TOKEN)


# states

class States:
    ask_mail = 1
    ask_password = 2
    ask_name = 3
    ask_link = 4
    complete = 5
    change_name = 6
    change_link = 7
    change_work = 8
    change_about = 9
    change_user_for_ask_id_admin = 10

# general functions


def help(message):
    user_id = message.from_user.id
    next_state = States.complete

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 1

    keyboard.add(
        types.InlineKeyboardButton(
            text='Посмотреть свой профиль',
            callback_data='show_profile'
        ),
        types.InlineKeyboardButton(
            text='Поменять данные профиля',
            callback_data='change_profile'
        ),
        types.InlineKeyboardButton(
            text='Поставить на паузу',
            callback_data='set_pause'
        ),
        types.InlineKeyboardButton(
            text='Снять c паузы',
            callback_data='set_run'
        )
    )

    user = get_user(user_id)
    if user.is_admin:
        keyboard.add(
            types.InlineKeyboardButton(
                text='Участники',
                callback_data='show_users'
            ),
            types.InlineKeyboardButton(
                text='Настройки пользователя',
                callback_data='change_user'
            ),
            types.InlineKeyboardButton(
                text='Пары',
                callback_data='show_pairs'
            ),
            types.InlineKeyboardButton(
                text='Сгенерировать пары',
                callback_data='generate_pairs'
            ),
            types.InlineKeyboardButton(
                text='Отправить приглашения',
                callback_data='send_invites'
            )
        )

    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, 'Выбери подходящую опцию ниже',
                     reply_markup=keyboard)
    bot.set_state(user_id, next_state)


# admin callbacks

@bot.message_handler(state=States.change_user_for_ask_id_admin)
def ask_mail_handler(message):
    user_id = message.from_user.id
    next_state = States.complete

    telegram_id = message.text

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 1

    user = get_user(telegram_id)
    if not user:
        answer = ('Не знаю такого пользователя')
    else:
        answer = (
            f'Настройки пользователя [{user.name}](tg://user?id={user.telegram_id})')
        keyboard.add(
            types.InlineKeyboardButton(
                text='Посмотреть профиль',
                callback_data=f'show_profile_for_admin_{user.telegram_id}'
            ),
            types.InlineKeyboardButton(
                text='Заблокировать',
                callback_data=f'refuse_{user.telegram_id}'
            ),
            types.InlineKeyboardButton(
                text='Поставить на паузу',
                callback_data=f'set_pause_for_admin_{user.telegram_id}'
            ),
            types.InlineKeyboardButton(
                text='Снять c паузы',
                callback_data=f'set_run_for_admin_{user.telegram_id}'
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.callback_query_handler(func=lambda call: call.data.startswith('show_profile_for_admin_'))
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    target_user_id = call.data[len('show_profile_for_admin_'):]

    answer = ('👉 Посмотреть профиль')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    user = get_user(target_user_id)
    answer = (
        'Вот так будет выглядеть твой профиль для собеседника:\n\n'
        f'{user}'
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help_from_show_profile'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('refuse_'))
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    target_user_id = call.data[len('refuse_'):]

    answer = ('👉 Убрать подтверждение')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    set_field(target_user_id, 'is_verified', False)
    set_field(target_user_id, 'password', generate_password())
    bot.send_message(
        target_user_id, 'Ваш аккаунт заблокирован!\nДля повторной регистрации напишите /start')

    answer = ('Пользователь заблокирован')

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_pause_for_admin_'))
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    target_user_id = call.data[len('set_pause_for_admin_'):]

    answer = ('👉 Поставить на паузу')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    set_field(target_user_id, 'is_active', False)
    bot.send_message(target_user_id, 'Админ поставил тебя на паузу')
    answer = ('Пользователь на паузе')

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_run_for_admin_'))
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    target_user_id = call.data[len('set_run_for_admin_'):]

    answer = ('👉 Снять c паузы')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    set_field(target_user_id, 'is_active', True)
    answer = ('Пользователь запущен')
    bot.send_message(target_user_id, 'Админ включил тебя во встречи')

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'show_users')
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    answer = ('👉 Участники')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    users = get_users()
    answer = (
        '\n'.join(
            [f'[{user.name}](tg://user?id={user.telegram_id}) - {user.telegram_id} - {"Verified" if user.is_verified else "Blocked"} - {"Run" if user.is_active else "Pause"} - {user.password}' for user in users])
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'change_user')
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    next_state = States.change_user_for_ask_id_admin

    answer = ('👉 Настройки пользователя')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = 'Введи номер пользователя'

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.callback_query_handler(func=lambda call: call.data == 'show_pairs')
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    answer = ('👉 Пары')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    pairs = get_pairs()
    if pairs:
        answer = (
            '\n'.join(
                [f'[{get_user(pair.user_a).name}](tg://user?id={get_user(pair.user_a).telegram_id}) - [{get_user(pair.user_b).name}](tg://user?id={get_user(pair.user_b).telegram_id})' if pair.user_b !=
                 '' else f'[{get_user(pair.user_a).name}](tg://user?id={get_user(pair.user_a).telegram_id}) - None' for pair in pairs]
            )
        )
    else:
        answer = 'Пар нету'

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


def generate_pairs():
    all_active_users = get_active_users()
    delete_pairs()
    random.shuffle(all_active_users)
    pairs = [all_active_users[i:i + 2]
             for i in range(0, len(all_active_users), 2)]
    for pair in pairs:
        if len(pair) == 2:
            create_pair(pair[0].telegram_id, pair[1].telegram_id)
        else:
            create_pair(pair[0].telegram_id, '')


@bot.callback_query_handler(func=lambda call: call.data == 'generate_pairs')
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    answer = ('👉 Сгенерировать пары')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    generate_pairs()

    answer = (
        'Сгенерировал пары'
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


def send_invites():
    for pair in get_pairs():
        if pair.user_b:
            bot.send_message(
                pair.user_a, f'Твоя пара!\n\n{get_user(pair.user_b)}', parse_mode='Markdown')
            bot.send_message(
                pair.user_b, f'Твоя пара!\n\n{get_user(pair.user_a)}', parse_mode='Markdown')
        else:
            bot.send_message(
                pair.user_a, f'Привет!\n\nНа этой неделе пары не нашлось😞', parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'send_invites')
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    send_invites()

    answer = ('👉 Отправить приглашения')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = (
        'Отправил приглашения'
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)

# user commands


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    next_state = States.ask_mail

    user = get_user(user_id)
    if (not user or not user.is_verified) and message.from_user.username not in ADMINS:
        create_user(user_id)

        answer = ('Привет!🤩\n'
                  'Я Random Coffee бот 🤖\n\n'
                  'Каждую неделю я буду предлагать '
                  'тебе для встречи интересного человека, '
                  'случайно выбранного среди '
                  'других участников🎲\n\n'
                  'Введи свой корпоративный mail, '
                  'чтобы получить пароль📧')
    elif not user and message.from_user.username in ADMINS:
        create_user(user_id)
        set_field(user_id, 'is_admin', True)
        set_field(user_id, 'is_verified', True)

        answer = ('Привет, админ!⭐\n\n'
                  'Как тебя зовут?☕️')
        next_state = States.ask_name
    else:
        answer = ('Рад тебя видеть!🔥\n'
                  'Если есть вопросы - /help')
        next_state = States.complete

    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer)
    bot.set_state(user_id, next_state)


@bot.message_handler(state=States.ask_mail)
def ask_mail_handler(message):
    user_id = message.from_user.id
    next_state = States.ask_password

    mail = message.text

    if is_correct_mail(mail):
        set_field(user_id, 'mail', mail)
        admins = get_admins()
        user = get_user(user_id)
        for admin in admins:
            answer_to_admin = (
                'Новый пользователь!\n'
                f'@{message.from_user.username}\n'
                f'[{message.from_user.first_name}](tg://user?id={user.telegram_id})\n'
                f'{user.mail}\n'
                f'{user.password}'
            )

            bot.send_message(admin.telegram_id,
                             answer_to_admin, parse_mode='Markdown')

    if is_correct_mail(mail) and SMTP:
        answer = ('Отправил📮\n'
                  'Введи пароль из письма🔑')
    elif is_correct_mail(mail) and not SMTP:
        answer = ('Напиши админу, '
                  f'чтобы получить пароль ({", ".join(["@"+i for i in ADMINS])})🛡️\n'
                  'И введи его сюда🔑')
    else:
        answer = ('Введи свой корпоративный mail, '
                  'чтобы получить пароль📧')
        next_state = States.ask_mail

    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer)
    bot.set_state(user_id, next_state)


@bot.message_handler(state=States.ask_password)
def ask_password_handler(message):
    user_id = message.from_user.id
    next_state = States.ask_name

    password = message.text
    user = get_user(user_id)

    if user.password == password:
        answer = ('Ты в системе🌐\n\n'
                  'Как тебя зовут?☕️')
        set_field(user_id, 'is_verified', True)
    else:
        answer = ('Попробуй еще раз\n')
        next_state = States.ask_password

    bot.send_message(user_id, answer)
    bot.set_state(user_id, next_state)


@bot.message_handler(state=States.ask_name)
def ask_name_handler(message):
    user_id = message.from_user.id
    next_state = States.ask_link

    name = message.text

    answer = ('Рад познакомиться!)\n\n'
              'Пришли ссылку на свой профиль '
              'в любой социальной сети. '
              'Так вы в паре сможете лучше узнать '
              'друг о друге до встречи🔎')

    set_field(user_id, 'name', name)

    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer)
    bot.set_state(user_id, next_state)


@bot.message_handler(state=States.ask_link)
def ask_link_handler(message):
    user_id = message.from_user.id
    next_state = States.complete

    link = message.text

    answer = ('Отлично, все готово!✨\n\n'
              'Свою пару для встречи ты будешь узнавать'
              ' каждый понедельник — сообщение придет в этот чат\n\n'
              'Напиши партнеру в Telegram, '
              'чтобы договориться о встрече или звонке\n'
              'Время и место вы выбираете сами\n\n'
              'Если остались вопросы - /help!)')

    set_field(user_id, 'link', link)

    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer)
    bot.set_state(user_id, next_state)


@bot.message_handler(commands=['help'])
def help_handler(message):
    user_id = message.from_user.id

    user = get_user(user_id)
    if user and user.is_verified:
        help(message)
    else:
        start_handler(message)


@bot.message_handler(state=States.change_name)
def change_name_handler(message):
    user_id = message.from_user.id
    next_state = States.complete

    name = message.text

    answer = 'Готово'

    set_field(user_id, 'name', name)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.message_handler(state=States.change_link)
def change_link_handler(message):
    user_id = message.from_user.id
    next_state = States.complete

    link = message.text

    answer = 'Готово'

    set_field(user_id, 'link', link)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.message_handler(state=States.change_work)
def change_work_handler(message):
    user_id = message.from_user.id
    next_state = States.complete

    work = message.text

    answer = 'Готово'

    set_field(user_id, 'work', work)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.message_handler(state=States.change_about)
def change_about_handler(message):
    user_id = message.from_user.id
    next_state = States.complete

    about = message.text

    answer = 'Готово'

    set_field(user_id, 'about', about)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)

# user callbacks


@bot.callback_query_handler(func=lambda call: call.data in ['help', 'help_from_show_profile'])
def change_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    answer = call.message.text
    print(answer)

    if call.data == 'help_from_show_profile':
        user = get_user(user_id)
        answer = (
            'Вот так будет выглядеть твой профиль для собеседника:\n\n'
            f'{user}'
        )

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer,
        parse_mode='Markdown'
    )

    help(call)


@bot.callback_query_handler(func=lambda call: call.data == 'show_profile')
def show_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    answer = ('👉 Хочу посмотреть свой профиль')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    user = get_user(user_id)
    answer = (
        'Вот так будет выглядеть твой профиль для собеседника:\n\n'
        f'{user}'
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help_from_show_profile'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'change_name')
def change_name_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    next_state = States.change_name

    answer = ('👉 Своё имя')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = ('Введи свое имя')

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.callback_query_handler(func=lambda call: call.data == 'change_link')
def change_link_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    next_state = States.change_link

    answer = ('👉 Ссылку на социальную сеть')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = ('Введи новую ссылку')

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.callback_query_handler(func=lambda call: call.data == 'change_work')
def change_work_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    next_state = States.change_work

    answer = ('👉 Кем работаю')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = ('Напиши, чем ты занимаешься по работе')

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.callback_query_handler(func=lambda call: call.data == 'change_about')
def change_about_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    next_state = States.change_about

    answer = ('👉 О себе')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = ('Напиши  новое описание:'
              ' пара предложений о твоих профессиональных'
              ' интересах, взглядах, хобби')

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.callback_query_handler(func=lambda call: call.data == 'change_profile')
def change_profile_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    next_state = States.complete

    answer = ('👉 Поменять данные профиля')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = ('Что хочешь поменять?')

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 1

    keyboard.add(
        types.InlineKeyboardButton(
            text='Своё имя',
            callback_data='change_name'
        ),
        types.InlineKeyboardButton(
            text='Ссылку на социальную сеть',
            callback_data='change_link'
        ),
        types.InlineKeyboardButton(
            text='Кем работаю',
            callback_data='change_work'
        ),
        types.InlineKeyboardButton(
            text='О себе',
            callback_data='change_about'
        ),
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)
    bot.set_state(user_id, next_state)


@bot.callback_query_handler(func=lambda call: call.data == 'set_pause')
def set_pause_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    answer = ('👉 Поставить на паузу')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = ('Готово')

    set_field(user_id, 'is_active', False)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'set_run')
def set_run_callback(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    answer = ('👉 Снять с паузу')

    bot.send_chat_action(user_id, 'typing')
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=answer
    )

    answer = ('Готово')

    set_field(user_id, 'is_active', True)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data='help'
        )
    )
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, answer, reply_markup=keyboard)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())


def schedule_checker():
    try:
        while True:
            schedule.run_pending()
            sleep(1) 
    except Exception as e:
        print(e)


if __name__ == "__main__":
    schedule.every().sunday.at('12:00').do(generate_pairs)
    schedule.every().monday.at('12:00').do(send_invites)
    Thread(target=schedule_checker).start()

    bot.polling()
