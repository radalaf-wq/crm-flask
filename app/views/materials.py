from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Material
from app.utils.security import roles_required

bp = Blueprint("materials", __name__, url_prefix="/materials")


@bp.route("/")
@login_required
def list_materials():
    materials = Material.query.order_by(Material.name.asc()).all()
    return render_template("materials_list.html", materials=materials)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("admin", "manager")
def create_material():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        unit = request.form.get("unit", "").strip()
        price_per_unit = request.form.get("price_per_unit", "").strip()
        stock_quantity = request.form.get("stock_quantity", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Название материала обязательно", "danger")
            return redirect(url_for("materials.create_material"))
        if not unit:
            flash("Единица измерения обязательна", "danger")
            return redirect(url_for("materials.create_material"))
        if not price_per_unit:
            flash("Цена за единицу обязательна", "danger")
            return redirect(url_for("materials.create_material"))

        try:
            price = float(price_per_unit)
        except ValueError:
            flash("Некорректное значение цены", "danger")
            return redirect(url_for("materials.create_material"))

        qty = 0.0
        if stock_quantity:
            try:
                qty = float(stock_quantity)
            except ValueError:
                flash("Некорректное значение количества на складе", "danger")
                return redirect(url_for("materials.create_material"))

        material = Material(
            name=name,
            unit=unit,
            price_per_unit=price,
            stock_quantity=qty,
            description=description or None,
        )
        db.session.add(material)
        db.session.commit()

        flash("Материал создан", "success")
        return redirect(url_for("materials.list_materials"))

    return render_template("material_form.html")


@bp.route("/<int:material_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("admin", "manager")
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        unit = request.form.get("unit", "").strip()
        price_per_unit = request.form.get("price_per_unit", "").strip()
        stock_quantity = request.form.get("stock_quantity", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Название материала обязательно", "danger")
            return redirect(url_for("materials.edit_material", material_id=material.id))
        if not unit:
            flash("Единица измерения обязательна", "danger")
            return redirect(url_for("materials.edit_material", material_id=material.id))

        try:
            price = float(price_per_unit)
        except ValueError:
            flash("Некорректное значение цены", "danger")
            return redirect(url_for("materials.edit_material", material_id=material.id))

        qty = 0.0
        if stock_quantity:
            try:
                qty = float(stock_quantity)
            except ValueError:
                flash("Некорректное значение количества на складе", "danger")
                return redirect(url_for("materials.edit_material", material_id=material.id))

        material.name = name
        material.unit = unit
        material.price_per_unit = price
        material.stock_quantity = qty
        material.description = description or None

        db.session.commit()
        flash("Материал обновлён", "success")
        return redirect(url_for("materials.list_materials"))

    return render_template("material_form.html", material=material)


@bp.route("/<int:material_id>/delete", methods=["POST"])
@login_required
@roles_required("admin", "manager")
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    flash("Материал удалён", "success")
    return redirect(url_for("materials.list_materials"))
