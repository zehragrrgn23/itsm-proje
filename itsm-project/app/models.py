from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

# --- Sabit secim listeleri -------------------------------------------------

ROLE_ADMIN = "admin"
ROLE_AGENT = "agent"
ROLE_USER = "user"
ROLES = [ROLE_USER, ROLE_AGENT, ROLE_ADMIN]

STATUS_OPEN = "Acik"
STATUS_IN_PROGRESS = "Islemde"
STATUS_PENDING = "Beklemede"
STATUS_RESOLVED = "Cozuldu"
STATUS_CLOSED = "Kapatildi"
STATUSES = [STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_PENDING, STATUS_RESOLVED, STATUS_CLOSED]
OPEN_STATUSES = [STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_PENDING]

PRIORITY_LOW = "Dusuk"
PRIORITY_MEDIUM = "Orta"
PRIORITY_HIGH = "Yuksek"
PRIORITY_CRITICAL = "Kritik"
PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_CRITICAL]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_USER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requested_tickets = db.relationship(
        "Ticket", back_populates="requester",
        foreign_keys="Ticket.requester_id"
    )
    assigned_tickets = db.relationship(
        "Ticket", back_populates="assigned_agent",
        foreign_keys="Ticket.assigned_agent_id"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_agent(self):
        return self.role in (ROLE_AGENT, ROLE_ADMIN)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    tickets = db.relationship("Ticket", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), nullable=False, default=STATUS_OPEN)
    priority = db.Column(db.String(20), nullable=False, default=PRIORITY_MEDIUM)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    category = db.relationship("Category", back_populates="tickets")
    requester = db.relationship(
        "User", back_populates="requested_tickets", foreign_keys=[requester_id]
    )
    assigned_agent = db.relationship(
        "User", back_populates="assigned_tickets", foreign_keys=[assigned_agent_id]
    )
    comments = db.relationship(
        "Comment", back_populates="ticket",
        cascade="all, delete-orphan", order_by="Comment.created_at"
    )

    @property
    def is_open(self):
        return self.status in OPEN_STATUSES

    def __repr__(self):
        return f"<Ticket #{self.id} {self.title}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    ticket = db.relationship("Ticket", back_populates="comments")
    author = db.relationship("User")

    def __repr__(self):
        return f"<Comment #{self.id} on Ticket #{self.ticket_id}>"
