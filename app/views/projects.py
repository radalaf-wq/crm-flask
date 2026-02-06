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
        return redirect(url_for("projects.list_projects_projects"))

    return render_template("project_form.html")


@bp.route('/<int:id>')
def view_project(id):
    """Просмотр детальной информации о проекте"""
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)


@bp.route('/<int:id>/comment', methods=['POST'])
def add_comment(id):
    """Добавить комментарий к проекту"""
    from app.models import Comment
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        comment = Comment(
            text=request.form['text'],
            project_id=id,
            user_id=1  # TODO: заменить на current_user.id после авторизации
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен!', 'success')
    
    return redirect(url_for('projects.view_project', id=id))


@bp.route('/<int:id>/upload', methods=['POST'])
def upload_file(id):
    """Загрузить файл к проекту"""
    from app.models import Attachment
    import os
    from werkzeug.utils import secure_filename
    
    project = Project.query.get_or_404(id)
    
    if 'file' not in request.files:
        flash('Файл не выбран', 'error')
        return redirect(url_for('projects.view_project', id=id))
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран', 'error')
        return redirect(url_for('projects.view_project', id=id))
    
    if file:
        filename = secure_filename(file.filename)
        # Создаем папку для загрузок, если ее нет
        upload_folder = os.path.join('app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Сохраняем информацию о файле в БД
        attachment = Attachment(
            file_name=filename,
            file_path=f'uploads/{filename}',
            file_size=os.path.getsize(filepath),
            project_id=id,
            uploaded_by_id=1  # TODO: заменить на current_user.id
        )
        db.session.add(attachment)
        db.session.commit()
        flash(f'Файл {filename} успешно загружен!', 'success')
    
    return redirect(url_for('projects.view_project', id=id))
