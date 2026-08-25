from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import User
from app.forms import LoginForm, RegisterForm

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Hos geldin, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        flash("Kullanici adi veya sifre hatali.", "danger")

    return render_template("login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter(
            (User.username == form.username.data.strip()) | (User.email == form.email.data.strip())
        ).first()
        if existing:
            flash("Bu kullanici adi veya e-posta zaten kayitli.", "danger")
        else:
            user = User(username=form.username.data.strip(), email=form.email.data.strip())
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Kayit basarili, simdi giris yapabilirsiniz.", "success")
            return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Cikis yapildi.", "info")
    return redirect(url_for("auth.login"))
