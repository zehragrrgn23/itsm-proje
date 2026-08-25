from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models import Ticket, STATUSES, OPEN_STATUSES

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_agent:
        base_query = Ticket.query
    else:
        base_query = Ticket.query.filter_by(requester_id=current_user.id)

    stats = {
        "total": base_query.count(),
        "open": base_query.filter(Ticket.status.in_(OPEN_STATUSES)).count(),
        "resolved": base_query.filter_by(status="Cozuldu").count(),
        "closed": base_query.filter_by(status="Kapatildi").count(),
    }

    status_counts = {
        status: base_query.filter_by(status=status).count() for status in STATUSES
    }

    recent_tickets = base_query.order_by(Ticket.created_at.desc()).limit(6).all()

    unassigned_count = None
    if current_user.is_agent:
        unassigned_count = Ticket.query.filter(
            Ticket.assigned_agent_id.is_(None), Ticket.status.in_(OPEN_STATUSES)
        ).count()

    return render_template(
        "dashboard.html",
        stats=stats,
        status_counts=status_counts,
        recent_tickets=recent_tickets,
        unassigned_count=unassigned_count,
    )
