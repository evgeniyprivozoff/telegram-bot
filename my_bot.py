from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import logging

# Этапы диалога
MODEL, COLOR, MILEAGE, BUDGET, PHONE = range(5)

# ID вашего канала или чата для отправки
USER_ID = 1392800811  # Замените на ваш ID

# Токен вашего бота
TOKEN = "7350155859:AAFGFBIKnupR60Y5etDdJd6l9wj1GS84lqE"

# Настроим логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Начало разговора
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Начало разговора с пользователем.")
    
    # Кнопка для начала нового опроса
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("Начать")]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    
    await update.message.reply_text(
        "Привет! Давайте начнем. Какую модель автомобиля вы выбираете?",
        reply_markup=reply_markup
    )
    return MODEL

# Сбор данных от пользователя
async def get_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Модель"] = update.message.text
    logger.info(f"Получена модель: {context.user_data['Модель']}")
    await update.message.reply_text("Какой цвет вас интересует?")
    return COLOR

async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Цвет"] = update.message.text
    logger.info(f"Получен цвет: {context.user_data['Цвет']}")
    await update.message.reply_text("Какой пробег вас устроит?")
    return MILEAGE

async def get_mileage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Пробег"] = update.message.text
    logger.info(f"Получен пробег: {context.user_data['Пробег']}")
    await update.message.reply_text("Какой у вас бюджет на автомобиль?")
    return BUDGET

async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Бюджет"] = update.message.text
    logger.info(f"Получен бюджет: {context.user_data['Бюджет']}")

    # Добавление кнопки для запроса номера телефона
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("Отправить номер телефона", request_contact=True)]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    await update.message.reply_text("Пожалуйста, отправьте ваш номер телефона.", reply_markup=reply_markup)
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Получен номер телефона.")
    if update.message.contact:
        context.user_data["Номер телефона"] = update.message.contact.phone_number
    else:
        context.user_data["Номер телефона"] = update.message.text

    # Логируем данные перед отправкой в канал
    user_data = context.user_data
    logger.info(f"Собраны данные: {user_data}")

    # Отправка заявки в личные сообщения
    await context.bot.send_message(
        chat_id=USER_ID,
        text=(
            f"Новая заявка:\n\n"
            f"Модель: {user_data['Модель']}\n"
            f"Цвет: {user_data['Цвет']}\n"
            f"Пробег: {user_data['Пробег']}\n"
            f"Бюджет: {user_data['Бюджет']}\n"
            f"Номер телефона: {user_data['Номер телефона']}"
        )
    )

    # Отправка благодарности клиенту
    await update.message.reply_text(
        "Спасибо за обращение, с вами свяжется менеджер в ближайшее время и сориентирует по всем вопросам."
    )

    # Завершаем разговор после отправки благодарности
    return ConversationHandler.END

# Обработчик выхода из диалога
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменен.")
    return ConversationHandler.END

# Основная функция для запуска бота
def main():
    app = Application.builder().token(TOKEN).build()

    # Настройка обработчика разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_model)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_color)],
            MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mileage)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Добавление обработчиков
    app.add_handler(conv_handler)

    # Запуск бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
