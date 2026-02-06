from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Material, Project, ProjectMaterial
from datetime import datetime

bp = Blueprint('materials', __name__, url_prefix='/materials')

@bp.route('/')
def list():
    """Список всех материалов"""
    materials = Material.query.order_by(Material.name).all()
    return render_template('materials_list.html', materials=materials)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Создание нового материала"""
    if request.method == 'POST':
        material = Material(
            name=request.form['name'],
            unit=request.form['unit'],
            unit_price=float(request.form['unit_price']) if request.form.get('unit_price') else 0,
            total_quantity=float(request.form['total_quantity']) if request.form.get('total_quantity') else 0,
            description=request.form.get('description', '')
        )
        db.session.add(material)
        db.session.commit()
        flash('Материал успешно создан!', 'success')
        return redirect(url_for('materials.list_materials'))
    
    return render_template('material_form.html', material=None)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Редактирование материала"""
    material = Material.query.get_or_404(id)
    
    if request.method == 'POST':
        material.name = request.form['name']
        material.unit = request.form['unit']
        material.unit_price = float(request.form['unit_price']) if request.form.get('unit_price') else 0
        material.total_quantity = float(request.form['total_quantity']) if request.form.get('total_quantity') else 0
        material.description = request.form.get('description', '')
        material.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Материал успешно обновлен!', 'success')
        return redirect(url_for('materials.list_materials'))
    
    return render_template('material_form.html', material=material)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Удаление материала"""
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash('Материал успешно удален!', 'success')
    return redirect(url_for('materials.list_materials'))

@bp.route('/project/<int:project_id>')
def project_materials(project_id):
    """Материалы для конкретного проекта"""
    project = Project.query.get_or_404(project_id)
    return render_template('project_materials.html', project=project)

@bp.route('/project/<int:project_id>/add', methods=['GET', 'POST'])
def add_to_project(project_id):
    """Добавить материал к проекту"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project_material = ProjectMaterial(
            project_id=project_id,
            material_id=int(request.form['material_id']),
            planned_quantity=float(request.form['planned_quantity']),
            used_quantity=float(request.form.get('used_quantity', 0)),
            notes=request.form.get('notes', '')
        )
        db.session.add(project_material)
        db.session.commit()
        flash('Материал добавлен к проекту!', 'success')
        return redirect(url_for('materials.project_materials', project_id=project_id))
    
    # Получаем все материалы для выбора
    all_materials = Material.query.order_by(Material.name).all()
    return render_template('project_material_form.html', project=project, materials=all_materials)
