from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Category, User, ROLES

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


@bp.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def categories():
    from app.forms import CategoryForm

    form = CategoryForm()
    if form.validate_on_submit():
        existing = Category.query.filter_by(name=form.name.data.strip()).first()
        if existing:
            flash("Bu kategori zaten mevcut.", "danger")
        else:
            category = Category(name=form.name.data.strip(), description=form.description.data.strip())
            db.session.add(category)
            db.session.commit()
            flash("Kategori eklendi.", "success")
        return redirect(url_for("admin.categories"))

    all_categories = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=all_categories, form=form)


@bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.tickets:
        flash("Bu kategoriye bagli talepler oldugu icin silinemez.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Kategori silindi.", "info")
    return redirect(url_for("admin.categories"))


@bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.username).all()
    return render_template("admin/users.html", users=all_users)


@bp.route("/users/<int:user_id>/role/<role>", methods=["POST"])
@login_required
@admin_required
def change_role(user_id, role):
    if role not in ROLES:
        abort(400)
    user = User.query.get_or_404(user_id)
    user.role = role
    db.session.commit()
    flash(f"{user.username} kullanicisinin rolu '{role}' olarak guncellendi.", "success")
    return redirect(url_for("admin.users"))
