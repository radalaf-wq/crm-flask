# app/__init__.py
import os
from flask import Flask
from .extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    # === базовая конфигурация ===
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Render кладёт строку подключения Postgres в DATABASE_URL
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///local.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # === инициализация расширений ===
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # куда редиректить неавторизованных

    # === user loader для Flask-Login ===
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # === регистрация моделей и blueprints ===
    with app.app_context():
        from . import models

        # ВРЕМЕННО: создать таблицы в БД на старте
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
        from flask import redirect, url_for
        return redirect(url_for("login"))

    # Пересоздать БД при каждом запуске
    with app.app_context():
        # Удаляем и пересоздаем таблицы принудительно
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Получаем список всех таблиц
        tables = inspector.get_table_names()
        
        # Удаляем все таблицы
        if tables:
            with db.engine.connect() as conn:
                conn.execute(db.text('DROP SCHEMA public CASCADE'))
                conn.execute(db.text('CREATE SCHEMA public'))
                conn.commit()
        
        # Создаем таблицы заново
        db.create_all()

    return app
