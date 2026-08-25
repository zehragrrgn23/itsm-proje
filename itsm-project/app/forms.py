from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField, SubmitField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo

from app.models import STATUSES, PRIORITIES


class LoginForm(FlaskForm):
    username = StringField("Kullanici Adi", validators=[DataRequired()])
    password = PasswordField("Sifre", validators=[DataRequired()])
    submit = SubmitField("Giris Yap")


class RegisterForm(FlaskForm):
    username = StringField("Kullanici Adi", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("E-posta", validators=[DataRequired(), Email()])
    password = PasswordField("Sifre", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Sifre Tekrar", validators=[DataRequired(), EqualTo("password", message="Sifreler eslesmiyor")]
    )
    submit = SubmitField("Kayit Ol")


class TicketForm(FlaskForm):
    title = StringField("Baslik", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Aciklama", validators=[DataRequired()])
    category_id = SelectField("Kategori", coerce=int, validators=[DataRequired()])
    priority = SelectField("Oncelik", choices=[(p, p) for p in PRIORITIES], validators=[DataRequired()])
    submit = SubmitField("Talebi Olustur")


class TicketUpdateForm(FlaskForm):
    status = SelectField("Durum", choices=[(s, s) for s in STATUSES], validators=[DataRequired()])
    priority = SelectField("Oncelik", choices=[(p, p) for p in PRIORITIES], validators=[DataRequired()])
    assigned_agent_id = SelectField("Atanan Personel", coerce=int)
    submit = SubmitField("Guncelle")


class CommentForm(FlaskForm):
    body = TextAreaField("Yorum", validators=[DataRequired()])
    submit = SubmitField("Yorum Ekle")


class CategoryForm(FlaskForm):
    name = StringField("Kategori Adi", validators=[DataRequired(), Length(max=80)])
    description = StringField("Aciklama", validators=[Length(max=255)])
    submit = SubmitField("Kaydet")
