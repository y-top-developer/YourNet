import telebot
from telebot import types, custom_filters

from settings import ADMINS, TELEGRAM_TOKEN, SMTP
from messages import generate_password, is_correct_mail
from orm import get_user, set_field, create_user

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

# general functions


def help(message):
    user_id = message.from_user.id

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
            text='Снять паузу',
            callback_data='set_run'
        )
    )

    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, 'Выбери подходящую опцию ниже', reply_markup=keyboard)

# user commands


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    next_state = States.ask_mail

    user = get_user(user_id)
    if not user or not user.is_verified:
        create_user(user_id)
        answer = ('Привет!🤩\n'
                  'Я Random Coffee бот 🤖\n\n'
                  'Каждую неделю я буду предлагать '
                  'тебе для встречи интересного человека, '
                  'случайно выбранного среди '
                  'других участников🎲\n\n'
                  'Введи свой корпоративный mail, '
                  'чтобы получить пароль📧')
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

    if is_correct_mail(mail) and SMTP:
        answer = ('Отправил📮\n'
                  'Введи пароль из письма🔑')

        set_field(user_id, 'mail', mail)
        set_field(user_id, 'password', generate_password())
    elif is_correct_mail(mail) and not SMTP:
        answer = ('Напиши админу, '
                  f'чтобы получить пароль ({", ".join(ADMINS)})🛡️\n'
                  'И введи его сюда🔑')
        set_field(user_id, 'mail', mail)
        set_field(user_id, 'password', generate_password())
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


@bot.message_handler(commands=['help'], state=[States.complete])
def help_handler(message):
    help(message)


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
    bot.send_message(user_id, answer, parse_mode='Markdown', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'change_name')
def change_profile_callback(call):
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
def change_profile_callback(call):
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
def change_profile_callback(call):
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
def change_profile_callback(call):
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

    answer = ('👉 Снять паузу')

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

if __name__ == "__main__":
    bot.polling()
