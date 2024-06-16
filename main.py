from image_tools import *
from config import *

import sqlite3
import telebot
import datetime

# telegram

bot = telebot.TeleBot(TOKEN)
lang = 'ru'
datas = {}
stack_datas = []
time = 15 * 60


@bot.message_handler(commands=['help'])
def help_msg(message):
    global datas, stack_datas
    if message.chat.id in datas:
        del datas[message.chat.id]
    while stack_datas and (stack_datas[0][0] - datetime.datetime.now()).seconds >= time:
        if stack_datas[0][1] in datas and datas[stack_datas[0][1]][1] != stack_datas[0][0]:
            break
        elif stack_datas[0][1] in datas:
            del datas[stack_datas[0][1]]
        stack_datas.pop(0)
    img = Image.open(r'sample.jpg')
    bot.send_message(message.chat.id, messages["help_message"])
    bot.send_photo(message.chat.id, photo=get_bytes_from_image(img))
    bot.send_message(message.chat.id, messages["send_photo_before"])
    bot.register_next_step_handler(message, photo_before)


@bot.message_handler(commands=['start'])
def menu(message):
    global datas, stack_datas
    if message.chat.id in datas:
        del datas[message.chat.id]
    while stack_datas and (stack_datas[0][0] - datetime.datetime.now()).seconds >= time:
        if stack_datas[0][1] in datas and datas[stack_datas[0][1]][1] != stack_datas[0][0]:
            break
        elif stack_datas[0][1] in datas:
            del datas[stack_datas[0][1]]
        stack_datas.pop(0)
    connection = sqlite3.connect('db')
    cursor = connection.cursor()

    cursor.execute('''SELECT ID FROM USERS WHERE ID=?''',
                   (message.chat.id,))
    user = cursor.fetchall()
    if len(user) == 0:
        bot.send_message(message.chat.id, messages["welcome_message"])
        img = Image.open('sample.jpg')
        bot.send_photo(message.chat.id, photo=get_bytes_from_image(img))
        cursor.execute('''INSERT INTO USERS (ID, NUMBER_OF_GENERATION) VALUES (?, 0)''',
                       (message.chat.id,))
        connection.commit()

    connection.close()

    bot.send_message(message.chat.id, messages["send_photo_before"])
    bot.register_next_step_handler(message, photo_before)


def photo_before(message):
    global datas, stack_datas
    if message.chat.id in datas:
        del datas[message.chat.id]
    while stack_datas and (stack_datas[0][0] - datetime.datetime.now()).seconds >= time:
        if stack_datas[0][1] in datas and datas[stack_datas[0][1]][1] != stack_datas[0][0]:
            break
        elif stack_datas[0][1] in datas:
            del datas[stack_datas[0][1]]
        stack_datas.pop(0)
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.photo is None:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    else:
        photo_id = message.photo[-1].file_id
        photo_file = bot.get_file(photo_id)
        photo_bytes = bot.download_file(photo_file.file_path)

        data = {"photo_before": photo_bytes}

        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, photo_before_text, data)


def photo_before_text(message, data):
    global datas, stack_datas
    if message.chat.id in datas:
        del datas[message.chat.id]
    while stack_datas and (stack_datas[0][0] - datetime.datetime.now()).seconds >= time:
        if stack_datas[0][1] in datas and datas[stack_datas[0][1]][1] != stack_datas[0][0]:
            break
        elif stack_datas[0][1] in datas:
            del datas[stack_datas[0][1]]
        stack_datas.pop(0)
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, photo_before_text, data)
    elif message.text is None:
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, photo_before_text, data)
    else:
        data['text_before'] = message.text
        bot.send_message(message.chat.id, messages["send_photo_after"])
        bot.register_next_step_handler(message, photo_after, data)


def photo_after(message, data):
    global datas, stack_datas
    if message.chat.id in datas:
        del datas[message.chat.id]
    while stack_datas and (stack_datas[0][0] - datetime.datetime.now()).seconds >= time:
        if stack_datas[0][1] in datas and datas[stack_datas[0][1]][1] != stack_datas[0][0]:
            break
        elif stack_datas[0][1] in datas:
            del datas[stack_datas[0][1]]
        stack_datas.pop(0)
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages["send_photo_after"])
        bot.register_next_step_handler(message, photo_after, data)
    elif message.photo is None:
        bot.send_message(message.chat.id, messages["send_photo_after"])
        bot.register_next_step_handler(message, photo_after, data)
    else:
        photo_id = message.photo[-1].file_id
        photo_file = bot.get_file(photo_id)
        photo_bytes = bot.download_file(photo_file.file_path)

        data['photo_after'] = photo_bytes

        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, photo_after_text, data)


def photo_after_text(message, data):
    global datas, stack_datas
    if message.chat.id in datas:
        del datas[message.chat.id]
    while stack_datas and (stack_datas[0][0] - datetime.datetime.now()).seconds >= time:
        if stack_datas[0][1] in datas and datas[stack_datas[0][1]][1] != stack_datas[0][0]:
            break
        elif stack_datas[0][1] in datas:
            del datas[stack_datas[0][1]]
        stack_datas.pop(0)
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, photo_after_text, data)
    elif message.text is None:
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, photo_after_text, data)
    else:
        data['text_after'] = message.text
        bot.send_message(message.chat.id, messages["comment"])
        bot.register_next_step_handler(message, all_text, data)


def send_photo(message, data):
    global datas, stack_datas
    new_image = create_image(data)
    time = datetime.datetime.now()
    datas[message.chat.id] = [data, time]
    stack_datas.append((time, message.chat.id))

    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="НОВЫЙ КОЛЛАЖ",
                                                     callback_data='save_data')
    button_change_photo_before = telebot.types.InlineKeyboardButton(text="Изменить ФОТО 'ДО'",
                                                                    callback_data='change_photo_before')
    button_change_text_before = telebot.types.InlineKeyboardButton(text="Изменить ПОДПИСЬ К ФОТО 'ДО'",
                                                                   callback_data='change_text_before')
    button_change_photo_after = telebot.types.InlineKeyboardButton(text="Изменить ФОТО 'ПОСЛЕ'",
                                                                   callback_data='change_photo_after')
    button_change_text_after = telebot.types.InlineKeyboardButton(text="Изменить ПОДПИСЬ К ФОТО 'ПОСЛЕ'",
                                                                  callback_data='change_text_after')
    button_change_text_all = telebot.types.InlineKeyboardButton(text="Изменить ЗАГОЛОВОК",
                                                                callback_data='change_text_all')
    keyboard.add(button_save, button_change_photo_before, button_change_text_before,
                 button_change_photo_after, button_change_text_after, button_change_text_all, row_width=1)

    bot.send_photo(message.chat.id, photo=get_bytes_from_image(new_image), reply_markup=keyboard)


def all_text(message, data):
    global datas, stack_datas
    if message.chat.id in datas:
        del datas[message.chat.id]
    while stack_datas and (stack_datas[0][0] - datetime.datetime.now()).seconds >= time:
        if stack_datas[0][1] in datas and datas[stack_datas[0][1]][1] != stack_datas[0][0]:
            break
        elif stack_datas[0][1] in datas:
            del datas[stack_datas[0][1]]
        stack_datas.pop(0)
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages["comment"])
        bot.register_next_step_handler(message, photo_after, data)
    elif message.text is None:
        bot.send_message(message.chat.id, messages["comment"])
        bot.register_next_step_handler(message, photo_after, data)
    else:
        data['all_text'] = message.text
        connection = sqlite3.connect('db')
        cursor = connection.cursor()

        cursor.execute('''SELECT NUMBER_OF_GENERATION FROM USERS WHERE ID=?''',
                       (message.chat.id,))
        number_of_generation = cursor.fetchall()[0][0]
        cursor.execute('''UPDATE USERS SET NUMBER_OF_GENERATION=? WHERE ID=?''',
                       (number_of_generation + 1, message.chat.id,))
        connection.commit()
        connection.close()
        send_photo(message, data)


@bot.callback_query_handler(
    func=lambda call: call.data == 'change_photo_before')
def change_photo_before_message(call):
    global datas
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                  reply_markup=None)
    if not (call.message.chat.id in datas):
        bot.send_message(call.message.chat.id, 'Сессия устарела')
        bot.send_message(call.message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(call.message, photo_before)
    else:
        bot.send_message(call.message.chat.id, 'Новое фото или измените формат кадра, лучше ближе к 3х4')
        bot.send_message(call.message.chat.id, messages['send_photo_before'])
        data = datas[call.message.chat.id][0]
        del datas[call.message.chat.id]
        bot.register_next_step_handler(call.message, change_photo_before, data)


def change_photo_before(message, data):
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_after, data)
    elif message.photo is None:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_after, data)
    else:
        photo_id = message.photo[-1].file_id
        photo_file = bot.get_file(photo_id)
        photo_bytes = bot.download_file(photo_file.file_path)

        data['photo_before'] = photo_bytes

        send_photo(message, data)


@bot.callback_query_handler(
    func=lambda call: call.data == 'change_photo_after')
def change_photo_after_message(call):
    global datas
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                  reply_markup=None)
    if not (call.message.chat.id in datas):
        bot.send_message(call.message.chat.id, 'Сессия устарела')
        bot.send_message(call.message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(call.message, photo_before)
    else:
        bot.send_message(call.message.chat.id, 'Новое фото или измените формат кадра, лучше ближе к 3х4')
        bot.send_message(call.message.chat.id, messages['send_photo_after'])
        data = datas[call.message.chat.id][0]
        del datas[call.message.chat.id]
        bot.register_next_step_handler(call.message, change_photo_after, data)


def change_photo_after(message, data):
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages["send_photo_after"])
        bot.register_next_step_handler(message, photo_after, data)
    elif message.photo is None:
        bot.send_message(message.chat.id, messages["send_photo_after"])
        bot.register_next_step_handler(message, photo_after, data)
    else:
        photo_id = message.photo[-1].file_id
        photo_file = bot.get_file(photo_id)
        photo_bytes = bot.download_file(photo_file.file_path)

        data['photo_after'] = photo_bytes

        send_photo(message, data)


@bot.callback_query_handler(
    func=lambda call: call.data == 'change_text_all')
def change_text_all_message(call):
    global datas
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                  reply_markup=None)
    if not (call.message.chat.id in datas):
        bot.send_message(call.message.chat.id, 'Сессия устарела')
        bot.send_message(call.message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(call.message, photo_before)
    else:
        bot.send_message(call.message.chat.id, messages['comment'])
        data = datas[call.message.chat.id][0]
        del datas[call.message.chat.id]
        bot.register_next_step_handler(call.message, change_text_all, data)


def change_text_all(message, data):
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages['comment'])
        bot.register_next_step_handler(message, change_text_all, data)
    elif message.text is None:
        bot.send_message(message.chat.id, messages['comment'])
        bot.register_next_step_handler(message, change_text_all, data)
    else:
        data['all_text'] = message.text
        send_photo(message, data)


@bot.callback_query_handler(
    func=lambda call: call.data == 'save_data')
def start_call(call):
    global datas
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                  reply_markup=None)
    if not (call.message.chat.id in datas):
        bot.send_message(call.message.chat.id, 'Сессия устарела')
        bot.send_message(call.message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(call.message, photo_before)
    else:
        del datas[call.message.chat.id]
        bot.send_message(call.message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(call.message, photo_before)


@bot.callback_query_handler(
    func=lambda call: call.data == 'change_text_after')
def change_text_after_message(call):
    global datas
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                  reply_markup=None)
    if not (call.message.chat.id in datas):
        bot.send_message(call.message.chat.id, 'Сессия устарела')
        bot.send_message(call.message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(call.message, photo_before)
    else:
        bot.send_message(call.message.chat.id, messages['send_text_before'])
        data = datas[call.message.chat.id][0]
        del datas[call.message.chat.id]
        bot.register_next_step_handler(call.message, change_text_after, data)


def change_text_after(message, data):
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, change_text_after, data)
    elif message.text is None:
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, change_text_after, data)
    else:
        data['text_after'] = message.text
        send_photo(message, data)


@bot.callback_query_handler(
    func=lambda call: call.data == 'change_text_before')
def change_text_before_message(call):
    global datas
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                  reply_markup=None)
    if not (call.message.chat.id in datas):
        bot.send_message(call.message.chat.id, 'Сессия устарела')
        bot.send_message(call.message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(call.message, photo_before)
    else:
        bot.send_message(call.message.chat.id, messages['send_text_before'])
        data = datas[call.message.chat.id][0]
        del datas[call.message.chat.id]
        bot.register_next_step_handler(call.message, change_text_before, data)


def change_text_before(message, data):
    if message.text == messages['start']:
        bot.send_message(message.chat.id, messages["send_photo_before"])
        bot.register_next_step_handler(message, photo_before)
    elif message.text == messages['help']:
        bot.send_message(message.chat.id, messages["help_message"])
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, change_text_before, data)
    elif message.text is None:
        bot.send_message(message.chat.id, messages['send_text_before'])
        bot.register_next_step_handler(message, change_text_before, data)
    else:
        data['text_before'] = message.text
        send_photo(message, data)


bot.infinity_polling()
