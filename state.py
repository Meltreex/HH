from aiogram.dispatcher.filters.state import State, StatesGroup

class AddApartment(StatesGroup):
    city = State()
    address = State()
    price = State()
    description = State()
    type = State()  # Вид квартиры
    area = State()  # Площадь
    photos = State()  # Фотографии

class SearchApartment(StatesGroup):
    current_index = State()  # Текущий индекс квартиры