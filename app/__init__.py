# app/__init__.py

import os

from flask import Flask, redirect, url_for
from sqlalchemy import inspect
from .extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    # === базовая конфигурация ===
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    app.config["TELEGRAM_BOT_TOKEN"] = os.environ.get("TELEGRAM_BOT_TOKEN")
    app.config["TELEGRAM_BOT_USERNAME"] = os.getenv("TELEGRAM_BOT_USERNAME", "CeeReeMbot")

    db_url = os.environ.get("DATABASE_URL", f"sqlite:///{app.instance_path}/crm.db")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # SQLite по умолчанию в dev
    if not db_url:
        os.makedirs(app.instance_path, exist_ok=True)
        db_url = f"sqlite:///{os.path.join(app.instance_path, 'crm.db')}"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # === расширения ===
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # === регистрация моделей и blueprints ===
    with app.app_context():
        from . import models  # noqa

        # ВРЕМЕННО: только если БД пустая — создать таблицы
        inspector = inspect(db.engine)
        if not inspector.get_table_names():
            db.create_all()

        from .views.dashboard import bp as dashboard_bp
        from .views.projects import bp as projects_bp
        from .views.tasks import bp as tasks_bp
        from .views.materials import bp as materials_bp
        from .views.auth import bp as auth_bp

        app.register_blueprint(dashboard_bp)
        app.register_blueprint(projects_bp)
        app.register_blueprint(tasks_bp)
        app.register_blueprint(materials_bp)
        app.register_blueprint(auth_bp)

    @app.route("/health")
    def health():
        return "OK"

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app
