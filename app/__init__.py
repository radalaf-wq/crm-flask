# app/__init__.py
import os
from flask import Flask
from .extensions import db


def create_app():
    app = Flask(__name__)

    # === базовая конфигурация ===
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Render кладёт строку подключения Postgres в DATABASE_URL
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Если вдруг DATABASE_URL нет — локально используем SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///local.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # === инициализация расширений ===
    db.init_app(app)

    # === регистрация моделей и blueprints ===
    with app.app_context():
        from . import models  # чтобы модели зарегистрировались

        # ВРЕМЕННО: создать таблицы в БД на старте
        db.create_all()

        from .views.dashboard import bp as dashboard_bp
                from .views.materials import bp as materials_bp
                        app.register_blueprint(materials_bp)
        from .views.projects import bp as projects_bp
        from .views.tasks import bp as tasks_bp
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(projects_bp)
        app.register_blueprint(tasks_bp)
    @app.route("/health")
    def health():
        return "OK"

    return app
