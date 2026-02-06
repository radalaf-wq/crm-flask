from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Task, Project, User
from datetime import datetime

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.route("/")
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("tasks_list.html", tasks=tasks)


@bp.route("/new", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        project_id = request.form.get("project_id", "").strip()
        status = request.form.get("status", "new")
        priority = request.form.get("priority", "normal")
        deadline_str = request.form.get("deadline", "").strip()

        if not title:
            flash("Название задачи обязательно", "danger")
            return redirect(url_for("tasks.create_task"))

        if not project_id:
            flash("Выберите проект", "danger")
            return redirect(url_for("tasks.create_task"))

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash("Некорректная дата дедлайна", "danger")

        task = Task(
            title=title,
            description=description or None,
            project_id=int(project_id),
            status=status,
            priority=priority,
            end_date=deadline,        )
        db.session.add(task)
        db.session.commit()
        flash("Задача создана", "success")
        return redirect(url_for("tasks.list_tasks_tasks"))

    # GET запрос - показываем форму
    projects = Project.query.filter_by(status="active").all()
    return render_template("task_form.html", projects=projects)
