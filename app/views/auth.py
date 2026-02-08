import hashlib
import hmac

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login")
def login():
    """Страница входа с Telegram Widget"""
    bot_username = current_app.config.get("TELEGRAM_BOT_USERNAME", "YourBotName")
    return render_template("login.html", bot_username=bot_username)


@bp.route("/telegram-callback", methods=["GET"])
def telegram_callback():
    """Обрабатываем данные от Telegram Login Widget"""
    bot_token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        flash("Telegram bot token не настроен", "danger")
        return redirect(url_for("auth.login"))

    # Получаем данные из query params
    auth_data = {
        "id": request.args.get("id"),
        "first_name": request.args.get("first_name"),
        "last_name": request.args.get("last_name"),
        "username": request.args.get("username"),
        "photo_url": request.args.get("photo_url"),
        "auth_date": request.args.get("auth_date"),
        "hash": request.args.get("hash"),
    }

    # Проверяем подпись от Telegram
    if not verify_telegram_auth(auth_data, bot_token):
        flash("Неверная подпись Telegram", "danger")
        return redirect(url_for("auth.login"))

    telegram_id = int(auth_data["id"])

    # Ищем пользователя в БД
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        # Если пользователя нет — создаём
        user = User(
            telegram_id=telegram_id,
            username=auth_data.get("username"),
            first_name=auth_data.get("first_name"),
            last_name=auth_data.get("last_name"),
            role="user",  # по умолчанию обычный пользователь
        )
        db.session.add(user)
        db.session.commit()
        flash("Добро пожаловать! Ваш аккаунт создан.", "success")

    # Логиним пользователя
    login_user(user)
    flash(f"Вы вошли как {user.first_name or user.username}", "success")
    return redirect(url_for("dashboard.index"))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("auth.login"))


@bp.route("/setup-admin/<int:telegram_id>")
def setup_admin(telegram_id):
    """Одноразовый эндпоинт для создания первого админа"""
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if user:
        user.role = "admin"
        db.session.commit()
        return f"User {telegram_id} теперь admin"
    return f"User {telegram_id} не найден", 404


def verify_telegram_auth(auth_data, bot_token):
    """Проверяем подпись Telegram Login Widget"""
    check_hash = auth_data.pop("hash", None)
    if not check_hash:
        return False

    # Формируем строку для проверки
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(auth_data.items()) if v is not None
    )

    # Создаём секретный ключ из токена бота
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_hash == check_hash
