import logging
from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from DataPostgre import dbworker
import KeyboardButton as kb
import config
from state import AddApartment, SearchApartment

BOT_TOKEN = config.BOT_TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

db = dbworker(host=config.host, user=config.user, password=config.password, db_name=config.db_name)

async def show_apartment(msg: types.Message, index: int, state: FSMContext):
    apartments = db.get_all_apartments()
    if not apartments:
        await msg.answer('Пока нет доступных квартир.')
        return

    # Проверяем, чтобы индекс был в пределах списка
    if index < 0:
        index = len(apartments) - 1
    elif index >= len(apartments):
        index = 0

    apartment = apartments[index]
    photos = apartment[8].split(';') if apartment[8] else []
    caption = (
        f"🏠 {apartment[3]}\n"
        f"📍 {apartment[2]}\n"
        f"💵 {apartment[4]} руб.\n"
        f"📝 {apartment[5]}\n"
        f"🛋 {apartment[6]}\n"
        f"📏 {apartment[7]} кв. м."
    )

    # Обновляем текущий индекс в состоянии
    await state.update_data(current_index=index)

    # Создаем inline-кнопки
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_kb.add(
        InlineKeyboardButton("Вперед ➡️", callback_data="next"),
        InlineKeyboardButton("Выйти ❌", callback_data="exit")
    )

    # Если есть фото, отправляем их как медиагруппу
    if photos:
        media_group = []
        for i, photo in enumerate(photos):
            if i == 0:
                # Первое фото с текстом
                media_group.append(InputMediaPhoto(media=photo, caption=caption))
            else:
                # Остальные фото без текста
                media_group.append(InputMediaPhoto(media=photo))
        await bot.send_media_group(msg.chat.id, media=media_group)
        # Отправляем inline-кнопки отдельным сообщением
        await msg.answer("Используйте кнопки для навигации:", reply_markup=inline_kb)
    else:
        # Если фото нет, отправляем только текст с inline-кнопками
        await msg.answer(caption, reply_markup=inline_kb)

@dp.message_handler(commands=['start'], state='*')
async def start(msg: types.Message):
    await msg.answer('Привет! Я помогу тебе найти арендную квартиру или добавить свою.', reply_markup=kb.start())
    if not db.user_exists(msg.from_user.id):
        db.add_user(msg.from_user.username, msg.from_user.id, msg.from_user.full_name)

@dp.message_handler(lambda msg: msg.text == 'Начать поиск🏠', state='*')
async def start_search(msg: types.Message, state: FSMContext):
    await state.update_data(current_index=0)  # Начинаем с первой квартиры
    await show_apartment(msg, 0, state)

# Обработчик для кнопки "Вперед ➡️"
@dp.callback_query_handler(lambda c: c.data == "next", state="*")
async def next_apartment(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    current_index = user_data.get('current_index', 0)
    await callback_query.answer()  # Подтверждаем нажатие кнопки
    await show_apartment(callback_query.message, current_index + 1, state)

# Обработчик для кнопки "Выйти ❌"
@dp.callback_query_handler(lambda c: c.data == "exit", state="*")
async def exit_search(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()  # Подтверждаем нажатие кнопки
    await state.finish()
    await callback_query.message.answer('Поиск завершен.', reply_markup=kb.start())

@dp.message_handler(lambda msg: msg.text == 'Добавить квартиру➕', state='*')
async def add_apartment_start(msg: types.Message):
    await msg.answer('Введите город:', reply_markup=kb.btn_cancel())
    await AddApartment.city.set()

@dp.message_handler(state=AddApartment.city)
async def add_apartment_city(msg: types.Message, state: FSMContext):
    await state.update_data(city=msg.text)
    await msg.answer('Введите адрес:')
    await AddApartment.next()

@dp.message_handler(state=AddApartment.address)
async def add_apartment_address(msg: types.Message, state: FSMContext):
    await state.update_data(address=msg.text)
    await msg.answer('Введите цену:')
    await AddApartment.next()

@dp.message_handler(state=AddApartment.price)
async def add_apartment_price(msg: types.Message, state: FSMContext):
    await state.update_data(price=msg.text)
    await msg.answer('Введите описание:')
    await AddApartment.next()

@dp.message_handler(state=AddApartment.description)
async def add_apartment_description(msg: types.Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await msg.answer('Введите вид квартиры (например, 1-комнатная):')
    await AddApartment.next()

@dp.message_handler(state=AddApartment.type)
async def add_apartment_type(msg: types.Message, state: FSMContext):
    await state.update_data(type=msg.text)
    await msg.answer('Введите площадь квартиры (например, 33.5 кв. м.):')
    await AddApartment.next()

@dp.message_handler(state=AddApartment.area)
async def add_apartment_area(msg: types.Message, state: FSMContext):
    await state.update_data(area=msg.text)
    await msg.answer('Отправьте фото квартиры (можно несколько):')
    await AddApartment.next()

@dp.message_handler(state=AddApartment.photos, content_types=types.ContentType.PHOTO)
async def add_apartment_photos(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photos = user_data.get('photos', [])  # Получаем уже добавленные фото
    photos.append(msg.photo[-1].file_id)  # Добавляем новое фото
    await state.update_data(photos=photos)
    await msg.answer('Фото добавлено. Отправьте ещё или нажмите "Готово".', reply_markup=kb.btn_finish_photos())

@dp.message_handler(lambda msg: msg.text == 'Готово✅', state=AddApartment.photos)
async def finish_adding_photos(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photos = ';'.join(user_data['photos'])  # Объединяем фото в строку с разделителем
    db.add_apartment(
        msg.from_user.id,
        user_data['city'],
        user_data['address'],
        user_data['price'],
        user_data['description'],
        user_data['type'],
        user_data['area'],
        photos
    )
    await msg.answer('Квартира успешно добавлена!', reply_markup=kb.start())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)