import hashlib
import hmac
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login")
def login():
    """Telegram Login Widget"""
    bot_username = current_app.config.get("TELEGRAM_BOT_USERNAME", "YourBotName")
    return render_template("login.html", bot_username=bot_username)


@bp.route("/telegram-callback", methods=["GET"])
def telegram_callback():
    """Telegram Login Widget callback"""
    bot_token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        flash("Telegram bot token not configured", "danger")
        return redirect(url_for("auth.login"))

    # Получаем параметры из Telegram
    auth_data = {
        "id": request.args.get("id"),
        "first_name": request.args.get("first_name"),
        "last_name": request.args.get("last_name"),
        "username": request.args.get("username"),
        "photo_url": request.args.get("photo_url"),
        "auth_date": request.args.get("auth_date"),
        "hash": request.args.get("hash"),
    }

    if not verify_telegram_auth(auth_data, bot_token):
        flash("Ошибка проверки Telegram данных", "danger")
        return redirect(url_for("auth.login"))

    telegram_id = int(auth_data["id"])

    # Поиск или создание пользователя
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=auth_data.get("username"),
            first_name=auth_data.get("first_name"),
            last_name=auth_data.get("last_name"),
            role="user",
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Добро пожаловать, {user.first_name or user.username}!", "success")
    else:
        flash(f"С возвращением, {user.first_name or user.username}!", "info")

    login_user(user)
    return redirect(url_for("dashboard.dashboard"))


@bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logout"""
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("auth.login"))


def verify_telegram_auth(auth_data, bot_token):
    """
    Проверяет подпись Telegram для безопасности.
    """
    check_hash = auth_data.pop("hash", None)
    if not check_hash:
        return False

    # Сортируем и объединяем параметры
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(auth_data.items()) if v is not None
    )

    # Создаём хеш
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    return hmac_hash == check_hash
