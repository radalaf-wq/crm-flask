# app/models.py
from datetime import datetime
from .extensions import db   # или from flask_sqlalchemy import SQLAlchemy; db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="worker")  # admin / manager / worker
    password_hash = db.Column(db.String(255), nullable=True)

    projects = db.relationship("Project", back_populates="owner", lazy="dynamic")
    tasks_assigned = db.relationship("Task", back_populates="assignee", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.id} {self.name}>"

class Project(db.Model):
        materials = db.relationship("ProjectMaterial", back_populates="project", lazy="dynamic")
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    client = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="active")  # active / on_hold / closed
    deadline = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    owner = db.relationship("User", back_populates="projects")

    tasks = db.relationship("Task", back_populates="project", lazy="dynamic")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Project {self.id} {self.name}>"

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.String(50),
        nullable=False,
        default="new",   # new / in_progress / done / canceled
        index=True,
    )
    priority = db.Column(
        db.String(20),
        nullable=False,
        default="normal",   # low / normal / high
        index=True,
    )
    deadline = db.Column(db.DateTime, nullable=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    project = db.relationship("Project", back_populates="tasks")

    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    assignee = db.relationship("User", back_populates="tasks_assigned")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    attachments = db.relationship("Attachment", back_populates="task", lazy="dynamic")

    def __repr__(self):
        return f"<Task {self.id} {self.title}>"

class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    task = db.relationship("Task", back_populates="attachments")

    file_name = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(512), nullable=False)  # путь/ключ на Яндекс.Диске/S3
    mime_type = db.Column(db.String(100), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Attachment {self.id} {self.file_name}>"


        class Material(db.Model):
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(50), nullable=False)  # м, шт, кг и т.п.
    unit_price = db.Column(db.Numeric(10, 2), nullable=True)  # цена за единицу
    total_quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # общее кол-во на складе
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # связь с ProjectMaterial
    project_materials = db.relationship("ProjectMaterial", back_populates="material", lazy="dynamic")

    def __repr__(self):
        return f"<Material {self.id} {self.name}>"


        class ProjectMaterial(db.Model):
    __tablename__ = "project_materials"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    project = db.relationship("Project", back_populates="materials")

    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False, index=True)
    material = db.relationship("Material", back_populates="project_materials")

    planned_quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # запланировано
    used_quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)     # использовано
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def remaining_quantity(self):
        """Вычисляемое поле: остаток = запланировано - использовано"""
        return self.planned_quantity - self.used_quantity

    def __repr__(self):
        return f"<ProjectMaterial {self.id} Project:{self.project_id} Material:{self.material_id}>"
