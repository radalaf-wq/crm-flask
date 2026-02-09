from flask import Blueprint, render_template
from flask_login import login_required

from app.models import Project, Task, Material

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("/")
@login_required
def dashboard():
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(status="active").count()
    closed_projects = Project.query.filter_by(status="closed").count()

    total_tasks = Task.query.count()
    tasks_to_do = Task.query.filter_by(status="to_do").count()
    tasks_in_progress = Task.query.filter_by(status="in_progress").count()
    tasks_done = Task.query.filter_by(status="done").count()

    total_materials = Material.query.count()

    return render_template(
        "dashboard.html",
        total_projects=total_projects,
        active_projects=active_projects,
        closed_projects=closed_projects,
        total_tasks=total_tasks,
        tasks_to_do=tasks_to_do,
        tasks_in_progress=tasks_in_progress,
        tasks_done=tasks_done,
        total_materials=total_materials,
    )
