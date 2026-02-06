import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://crm-flask-ricn.onrender.com')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение при получении команды /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}!\n\n"
        f"Добро пожаловать в CRM систему.\n\n"
        f"Для входа в систему перейдите по ссылке:\n"
        f"{WEBAPP_URL}/login"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение при получении команды /help"""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n\n"
        f"Веб-интерфейс: {WEBAPP_URL}"
    )

def main() -> None:
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("Не установлена переменная окружения TELEGRAM_BOT_TOKEN")
        return
    
    # Создаём приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
