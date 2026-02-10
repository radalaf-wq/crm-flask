from flask import Blueprint, render_template
from flask_login import login_required

from app.models import Project, Task, Material

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("/")
@login_required
def dashboard():
    counters = {
        'total_projects': Project.query.count(),
        'active_projects': Project.query.filter_by(status="active").count(),
        'closed_projects': Project.query.filter_by(status="closed").count(),
        'total_tasks': Task.query.count(),
        'tasks_to_do': Task.query.filter_by(status="to_do").count(),
        'tasks_in_progress': Task.query.filter_by(status="in_progress").count(),
        'tasks_done': Task.query.filter_by(status="done").count(),
        'total_materials': Material.query.count(),
        'high_priority': Task.query.filter_by(priority="high").count(),
        'medium_priority': Task.query.filter_by(priority="medium").count(),
        'low_priority': Task.query.filter_by(priority="low").count(),
    }

    return render_template("dashboard.html", counters=counters)
