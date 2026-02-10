from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Project, Comment

bp = Blueprint("projects", __name__, url_prefix="/projects")


@bp.route("/")
@login_required
def list_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects_list.html", projects=projects)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        client = request.form.get("client", "").strip()
        status = request.form.get("status", "active")
        deadline_str = request.form.get("deadline", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Название проекта обязательно", "danger")
            return redirect(url_for("projects.create_project"))

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash("Некорректная дата дедлайна", "danger")

        project = Project(
            name=name,
            client=client or None,
            status=status,
            deadline=deadline,
            description=description or None,
        )
        db.session.add(project)
        db.session.commit()

        flash("Проект создан", "success")
        return redirect(url_for("projects.list_projects"))

    return render_template("project_form.html")


@bp.route("/<int:project_id>")
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)


@bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        client = request.form.get("client", "").strip()
        status = request.form.get("status", project.status)
        deadline_str = request.form.get("deadline", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Название проекта обязательно", "danger")
            return redirect(url_for("projects.edit_project", project_id=project.id))

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash("Некорректная дата дедлайна", "danger")

        project.name = name
        project.client = client or None
        project.status = status
        project.deadline = deadline
        project.description = description or None

        db.session.commit()
        flash("Проект обновлён", "success")
        return redirect(url_for("projects.view_project", project_id=project.id))

    return render_template("project_form.html", project=project)


@bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Проект удалён", "success")
    return redirect(url_for("projects.list_projects"))


@bp.route("/<int:project_id>/comment", methods=["POST"])
@login_required
def add_comment(project_id):
    from flask_login import current_user
    
    project = Project.query.get_or_404(project_id)
    text = request.form.get("text", "").strip()

    if not text:
        flash("Текст комментария не может быть пустым", "danger")
        return redirect(url_for("projects.view_project", project_id=project.id))

    comment = Comment(
        text=text,
        project_id=project.id,
        user_id=current_user.id,
    )
    db.session.add(comment)
    db.session.commit()

    flash("Комментарий добавлен", "success")
    return redirect(url_for("projects.view_project", project_id=project.id))
