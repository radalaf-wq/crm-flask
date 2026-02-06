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
    # u0421u0432u044fu0437u044c u0441 u043cu0430u0442u0435u0440u0438u0430u043bu0430u043cu0438
    materials = db.relationship("ProjectMaterial", back_populates="project", lazy="dynamic")
    comments = db.relationship("Comment", back_populates="project", lazy="dynamic")
    attachments = db.relationship("Attachment", back_populates="project", lazy="dynamic")

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


# ========== Материалы ==========

class Material(db.Model):
    """Материал на складе"""
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    unit_price = db.Column(db.Float, default=0)
    total_quantity = db.Column(db.Float, default=0)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с проектами
    project_materials = db.relationship("ProjectMaterial", back_populates="material", lazy="dynamic")

    def __repr__(self):
        return f"Material {self.id} {self.name}"


class ProjectMaterial(db.Model):
    """Связь материалов с проектами"""
    __tablename__ = "project_materials"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = db.relationship("Project", back_populates="materials")

    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    material = db.relationship("Material", back_populates="project_materials")

    planned_quantity = db.Column(db.Float, nullable=False, default=0)
    used_quantity = db.Column(db.Float, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def remaining_quantity(self):
        return self.planned_quantity - self.used_quantity

    def __repr__(self):
        return f"ProjectMaterial {self.id} (Project {self.project_id}, Material {self.material_id})"


# ========== Комментарии ==========

class Comment(db.Model):
    """Комментарий к проекту"""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = db.relationship("Project", back_populates="comments")
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref="comments")
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Comment {self.id} on Project {self.project_id}"
