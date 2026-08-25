import click
from flask import Flask, render_template

from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.tickets import bp as tickets_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    register_cli(app)

    return app


def register_cli(app):
    @app.cli.command("seed-db")
    def seed_db():
        """Veritabani tablolarini olusturur ve baslangic verilerini ekler."""
        from app.models import User, Category, ROLE_ADMIN

        with app.app_context():
            db.create_all()

            if not User.query.filter_by(username=app.config["ADMIN_USERNAME"]).first():
                admin = User(
                    username=app.config["ADMIN_USERNAME"],
                    email=app.config["ADMIN_EMAIL"],
                    role=ROLE_ADMIN,
                )
                admin.set_password(app.config["ADMIN_PASSWORD"])
                db.session.add(admin)
                click.echo(f"Admin kullanici olusturuldu: {app.config['ADMIN_USERNAME']}")

            default_categories = [
                ("Donanim", "Bilgisayar, yazici, monitor vb. donanim talepleri"),
                ("Yazilim", "Uygulama kurulum/hata talepleri"),
                ("Ag / Network", "Internet, VPN, baglanti sorunlari"),
                ("Erisim Talebi", "Kullanici hesabi, yetki, sifre islemleri"),
                ("Diger", "Yukaridaki kategorilere girmeyen talepler"),
            ]
            for name, desc in default_categories:
                if not Category.query.filter_by(name=name).first():
                    db.session.add(Category(name=name, description=desc))

            db.session.commit()
            click.echo("Veritabani hazir.")
