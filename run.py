import threading
import os
from app import create_app
app = create_app()


def start_bot():
    """Запуск Telegram бота в отдельном потоке"""
    # Проверяем наличие токена
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("TELEGRAM_BOT_TOKEN не установлен. Бот не будет запущен.")
        return
    
    try:
        import bot
        bot.main()
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
if __name__ == "__main__":
    app.run(debug=True)


    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("Бот запущен в фоновом режиме")
    
    # Запускаем Flask приложение
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)