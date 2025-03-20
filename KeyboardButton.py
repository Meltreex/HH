from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def start():
    button_search = KeyboardButton('Начать поиск🏠')
    button_add = KeyboardButton('Добавить квартиру➕')
    menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return menu.add(button_search, button_add)

def btn_exit():
    button_exit = KeyboardButton('Выйти❌')
    menu_exit = ReplyKeyboardMarkup(resize_keyboard=True)
    return menu_exit.add(button_exit)

def btn_cancel():
    button_cancel = KeyboardButton('Отменить❌')
    button_cancel_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return button_cancel_menu.add(button_cancel)

def btn_finish_photos():
    button_finish = KeyboardButton('Готово✅')
    menu_finish = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return menu_finish.add(button_finish)