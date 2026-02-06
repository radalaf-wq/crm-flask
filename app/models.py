# app/models.py
from datetime import datetime
from flask_login import UserMixin
from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default="user")  # admin, manager, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    projects = db.relationship("Project", back_populates="owner")

    # Flask-Login требует эти методы
    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __repr__(self):
        return f"<User {self.telegram_id} ({self.username})>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    client = db.Column(db.String(255))
    status = db.Column(db.String(50), default="active")  # active, on_hold, closed
    deadline = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Связи
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", back_populates="projects")

    tasks = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")
    materials = db.relationship("ProjectMaterial", back_populates="project", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="project", cascade="all, delete-orphan")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Project {self.id} {self.name}>"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="to_do")  # to_do, in_progress, done
    priority = db.Column(db.String(50), default="medium")  # low, medium, high
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = db.relationship("Project", back_populates="tasks")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id} {self.title}>"


class Material(db.Model):
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(50), nullable=False)  # м, кг, шт и т.д.
    price_per_unit = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Float, default=0)
    description = db.Column(db.Text, nullable=True)

    project_materials = db.relationship("ProjectMaterial", back_populates="material")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Material {self.id} {self.name}>"


class ProjectMaterial(db.Model):
    __tablename__ = "project_materials"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Float, nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)

    project = db.relationship("Project", back_populates="materials")
    material = db.relationship("Material", back_populates="project_materials")

    def __repr__(self):
        return f"<ProjectMaterial {self.project_id}-{self.material_id}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    project = db.relationship("Project", back_populates="comments")
    user = db.relationship("User", backref="comments")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Comment {self.id} on Project {self.project_id}>"
