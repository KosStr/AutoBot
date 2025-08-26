import os
import json
from dotenv import load_dotenv
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

CLASS, BRAND_MODEL, PRICE, CATEGORY = range(4)

# Load environment variables from .env file
load_dotenv()

class TranslationHandler:
    def __init__(self):
        self.fuel_types = {
            'gas': 'Бензин',
            'diesel': 'Дизель',
            'hybrid': 'Гібрид',
            'electric': 'Електрика'
        }

        self.fuel_type_reverse = {v: k for k, v in self.fuel_types.items()}

    def get_fuel_type_display(self, internal_value: str) -> str:
        return self.fuel_types.get(internal_value.lower(), internal_value)

    def get_fuel_type_internal(self, display_value: str) -> str:
        return self.fuel_type_reverse.get(display_value.lower(), '')

    def get_fuel_type_buttons(self) -> list:
        return [[self.fuel_types['gas'], self.fuel_types['diesel']],
                [self.fuel_types['hybrid'], self.fuel_types['electric']]]

def load_car_data(folder: str):
    try:
        with open(f'{folder}/cars.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Головне Меню ⚙️", callback_data='start')],
        [InlineKeyboardButton("Пошук Авто 🔎", callback_data='search')],
        [InlineKeyboardButton("Скоро на Аукціоні 🚢", callback_data='auction')],
        [InlineKeyboardButton("Авто в Наявності 🚗", callback_data='market')],
        [InlineKeyboardButton("Наші Контакти 📇", callback_data='contacts')],
        [InlineKeyboardButton("Допомога ℹ️", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def class_keyboard():
    translator = TranslationHandler()
    return ReplyKeyboardMarkup(
        translator.get_fuel_type_buttons(),
        one_time_keyboard=True,
        resize_keyboard=True
    )

def price_keyboard():
    return ReplyKeyboardMarkup(
        [['5 - 10.000$', '10 - 15.000$'], ['15 - 20.000$', '20.000$ +']],
        one_time_keyboard=True,
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await update.message.reply_text(
        f"Привіт {user.first_name}! Вітаємо в LionMotors🦁 Боті. Що Bac цікавить?",
        reply_markup=main_menu_keyboard()
    )

async def display_cars(query: Update, context: ContextTypes.DEFAULT_TYPE, folder: str, message_prefix: str):
    translator = TranslationHandler()
    cars = load_car_data(folder)
    if not cars:
        await query.message.reply_text(text=f"Немає доступних автомобілів для {message_prefix}.", reply_markup=main_menu_keyboard())
        return

    for car in cars:
        fuel_type_display = translator.get_fuel_type_display(car['fuel_type'])

        message = (
            f"{car['year']} {car['make']} {car['model']}\n"
            f"Ціна: ${car['price']}\n"
            f"VIN: {car['vin']}\n"
            f"Стан: {car['condition']}\n"
            f"Пробіг: {car['mileage']} миль\n"
            f"Тип палива: {fuel_type_display}"
        )

        image_paths = car.get('image_paths', [])
        try:
            if image_paths:
                media = []
                valid_images = False
                for image_path in image_paths:
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as photo:
                            media.append(InputMediaPhoto(media=photo.read()))
                            valid_images = True
                    else:
                        message += f"\n[Фото не знайдено: {image_path}]"
                if valid_images:
                    await query.message.reply_media_group(media=media, caption=message)
                else:
                    await query.message.reply_text(message)
            else:
                await query.message.reply_text(f"{message}\n[Фото відсутні]")

        except Exception as e:
            await query.message.reply_text(f"{message}\n[Помилка завантаження фото: {str(e)}]")
    
    await query.message.reply_text(text=f"Показуємо автомобілі для {message_prefix}:", reply_markup=main_menu_keyboard())

async def display_filtered_cars(update: Update, context: ContextTypes.DEFAULT_TYPE, cars: list, message_prefix: str):
    translator = TranslationHandler()
    if not cars:
        await update.message.reply_text(text=f"Немає доступних автомобілів для {message_prefix} з даними фільтрами.", reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text(f"Показуємо автомобілі для {message_prefix}:", reply_markup=main_menu_keyboard())
        return

    for car in cars:
        fuel_type_display = translator.get_fuel_type_display(car['fuel_type'])
        message = (
            f"{car['year']} {car['make']} {car['model']}\n"
            f"Ціна: ${car['price']}\n"
            f"VIN: {car['vin']}\n"
            f"Стан: {car['condition']}\n"
            f"Пробіг: {car['mileage']} миль\n"
            f"Тип палива: {fuel_type_display}"
        )
        image_paths = car.get('image_paths', [])
        try:
            if image_paths:
                media = []
                valid_images = False
                for image_path in image_paths:
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as photo:
                            media.append(InputMediaPhoto(media=photo.read()))
                            valid_images = True
                    else:
                        message += f"\n[Фото не знайдено: {image_path}]"
                if valid_images:
                    await update.message.reply_media_group(media=media, caption=message)
                else:
                    await update.message.reply_text(message)
            else:
                await update.message.reply_text(f"{message}\n[Фото відсутні]")
        except Exception as e:
            await update.message.reply_text(f"{message}\n[Помилка завантаження фото: {str(e)}]")
    
    await update.message.reply_text(f"Показуємо автомобілі для {message_prefix}:", reply_markup=main_menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        user = query.from_user
        await query.message.reply_text(
            f"Привіт {user.first_name}! Вітаємо в LionMotors🦁 Боті. Що Bac цікавить?",
            reply_markup=main_menu_keyboard()
        )
    elif query.data == 'search':
        await query.message.reply_text("Виберіть тип пального", reply_markup=class_keyboard())
        return CLASS
    elif query.data == 'market':
        await display_cars(query, context, 'market_cars', 'market')
    elif query.data == 'auction':
        await display_cars(query, context, 'auction_cars', 'auction')
    elif query.data == 'contacts':
        await query.message.reply_text(text="Зв'яжіться з нами: info@lionmotors.com", reply_markup=main_menu_keyboard())
    elif query.data == 'help':
        await query.message.reply_text(text="Використовуйте меню для перегляду автомобілів або зв'язку з нами!", reply_markup=main_menu_keyboard())

async def get_class(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    translator = TranslationHandler()
    text = update.message.text.strip().lower()
    internal_fuel_type = translator.get_fuel_type_internal(text)
    if not internal_fuel_type:
        await update.message.reply_text("Будь ласка, виберіть один із: Дизель, Бензин, Гібрид, Електрика.", reply_markup=class_keyboard())
        return CLASS
    context.user_data['fuel_type'] = internal_fuel_type
    keyboard = ReplyKeyboardMarkup([['Пропустити']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Введіть марку або модель для фільтрації, або натисніть Пропустити:", reply_markup=keyboard)
    return BRAND_MODEL

async def get_brand_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    if text != 'пропустити':
        context.user_data['brand_model'] = text
    await update.message.reply_text("Виберіть діапазон цін:", reply_markup=price_keyboard())
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    if text == '5 - 10.000$':
        min_p, max_p = 5000, 10000
    elif text == '10 - 15.000$':
        min_p, max_p = 10000, 15000
    elif text == '15 - 20.000$':
        min_p, max_p = 15000, 20000
    elif text == '20.000$ +':
        min_p, max_p = 20000, float('inf')
    else:
        await update.message.reply_text("Виберіть Ціновий Діапазон 💵", reply_markup=price_keyboard())
        return PRICE
    context.user_data['min_price'] = min_p
    context.user_data['max_price'] = max_p
    keyboard = ReplyKeyboardMarkup([['Market', 'Auction']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Choose to show from Market or Auction:", reply_markup=keyboard)
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    if text == 'market':
        folder = 'market_cars'
        prefix = 'market'
    elif text == 'auction':
        folder = 'auction_cars'
        prefix = 'auction'
    else:
        await update.message.reply_text("Please choose 'Market' or 'Auction'.", reply_markup=ReplyKeyboardMarkup([['Market', 'Auction']], one_time_keyboard=True, resize_keyboard=True))
        return CATEGORY

    cars = load_car_data(folder)
    filtered_cars = []
    fuel_type = context.user_data.get('fuel_type')
    brand_model = context.user_data.get('brand_model')
    min_price = context.user_data.get('min_price')
    max_price = context.user_data.get('max_price')

    for car in cars:
        if fuel_type and car.get('fuel_type', '').lower() != fuel_type:
            continue
        if brand_model:
            if brand_model not in car['make'].lower() and brand_model not in car['model'].lower():
                continue
        if min_price is not None and car['price'] < min_price:
            continue
        if max_price is not None and car['price'] > max_price:
            continue
        filtered_cars.append(car)

    context.user_data.clear()
    await display_filtered_cars(update, context, filtered_cars, prefix)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Search cancelled.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^(start|search|market|auction|contacts|help)$')],
        states={
            CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_class)],
            BRAND_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_brand_model)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()