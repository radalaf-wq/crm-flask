from flask import Blueprint, render_template
from sqlalchemy import func
from app.extensions import db
from app.models import Project, Task
from datetime import datetime

bp = Blueprint("dashboard", __name__)

def get_dashboard_counters():
    total_projects = db.session.query(func.count(Project.id)).scalar()
    total_tasks = db.session.query(func.count(Task.id)).scalar()
    tasks_overdue = (
        db.session.query(func.count(Task.id))
        .filter(
            Task.status != "done",
            Task.deadline != None,
            Task.deadline < datetime.utcnow(),
        )
        .scalar()
    )
    return {
        "total_projects": total_projects or 0,
        "total_tasks": total_tasks or 0,
        "tasks_overdue": tasks_overdue or 0,
    }

@bp.route("/")
def index():
    counters = get_dashboard_counters()
    return render_template("dashboard.html", counters=counters)
