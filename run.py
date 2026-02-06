import threading
import os
from app import create_app

app = create_app()

def start_bot():
    """Запуск Telegram бота в отдельном потоке"""
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("Токен бота не установлен")
        return
    
    try:
        import bot
        bot.main()
    except Exception as e:
        print(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    # Запускаем бота в фоновом режиме
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("Бот запущен в фоновом режиме")
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
