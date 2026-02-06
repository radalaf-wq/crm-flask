from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Project
from datetime import datetime

bp = Blueprint("projects", __name__, url_prefix="/projects")


@bp.route("/")
def list_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects_list.html", projects=projects)


@bp.route("/new", methods=["GET", "POST"])
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
