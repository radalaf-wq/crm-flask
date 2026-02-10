from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Task, Project

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.route("/")
@login_required
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("tasks_list.html", tasks=tasks)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        project_id = request.form.get("project_id", "").strip()
        status = request.form.get("status", "to_do")
        priority = request.form.get("priority", "medium")
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
            end_date=deadline,
        )
        db.session.add(task)
        db.session.commit()

        flash("Задача создана", "success")
        return redirect(url_for("tasks.list_tasks"))

    projects = Project.query.filter_by(status="active").all()
    return render_template("task_form.html", projects=projects)


@bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", task.status)
        priority = request.form.get("priority", task.priority)
        deadline_str = request.form.get("deadline", "").strip()

        if not title:
            flash("Название задачи обязательно", "danger")
            return redirect(url_for("tasks.edit_task", task_id=task.id))

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash("Некорректная дата дедлайна", "danger")

        task.title = title
        task.description = description or None
        task.status = status
        task.priority = priority
        task.end_date = deadline

        db.session.commit()
        flash("Задача обновлена", "success")
        return redirect(url_for("tasks.list_tasks"))

    projects = Project.query.filter_by(status="active").all()
    return render_template("task_form.html", task=task, projects=projects)


@bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Задача удалена", "success")
    return redirect(url_for("tasks.list_tasks"))
