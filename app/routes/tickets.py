from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Ticket, Category, Comment, User, STATUSES, PRIORITIES, ROLE_AGENT, ROLE_ADMIN
from app.forms import TicketForm, TicketUpdateForm, CommentForm

bp = Blueprint("tickets", __name__, url_prefix="/tickets")


def agent_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_agent:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


@bp.route("/")
@login_required
def list_tickets():
    query = Ticket.query

    if not current_user.is_agent:
        query = query.filter_by(requester_id=current_user.id)

    status = request.args.get("status")
    priority = request.args.get("priority")
    category_id = request.args.get("category_id", type=int)
    only_mine = request.args.get("only_mine")

    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if only_mine and current_user.is_agent:
        query = query.filter_by(assigned_agent_id=current_user.id)

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Ticket.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "tickets/list.html",
        pagination=pagination,
        tickets=pagination.items,
        categories=categories,
        statuses=STATUSES,
        priorities=PRIORITIES,
        current_filters={
            "status": status or "",
            "priority": priority or "",
            "category_id": category_id or "",
            "only_mine": only_mine or "",
        },
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create_ticket():
    form = TicketForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if not form.category_id.choices:
        flash("Once en az bir kategori tanimlanmali. Lutfen yonetici ile iletisime gecin.", "warning")

    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            category_id=form.category_id.data,
            priority=form.priority.data,
            requester_id=current_user.id,
        )
        db.session.add(ticket)
        db.session.commit()
        flash(f"#{ticket.id} numarali talebiniz olusturuldu.", "success")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return render_template("tickets/create.html", form=form)


@bp.route("/<int:ticket_id>", methods=["GET", "POST"])
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if not current_user.is_agent and ticket.requester_id != current_user.id:
        abort(403)

    comment_form = CommentForm()
    update_form = None

    if current_user.is_agent:
        update_form = TicketUpdateForm(status=ticket.status, priority=ticket.priority)
        agents = User.query.filter(User.role.in_([ROLE_AGENT, ROLE_ADMIN])).order_by(User.username).all()
        update_form.assigned_agent_id.choices = [(0, "Atanmamis")] + [(a.id, a.username) for a in agents]
        if not update_form.assigned_agent_id.data:
            update_form.assigned_agent_id.data = ticket.assigned_agent_id or 0

    if request.method == "POST" and "body" in request.form and comment_form.validate_on_submit():
        comment = Comment(body=comment_form.body.data.strip(), ticket_id=ticket.id, author_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash("Yorum eklendi.", "success")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return render_template(
        "tickets/detail.html", ticket=ticket, comment_form=comment_form, update_form=update_form
    )


@bp.route("/<int:ticket_id>/update", methods=["POST"])
@login_required
@agent_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    form = TicketUpdateForm()
    agents = User.query.filter(User.role.in_([ROLE_AGENT, ROLE_ADMIN])).order_by(User.username).all()
    form.assigned_agent_id.choices = [(0, "Atanmamis")] + [(a.id, a.username) for a in agents]

    if form.validate_on_submit():
        from datetime import datetime

        ticket.status = form.status.data
        ticket.priority = form.priority.data
        ticket.assigned_agent_id = form.assigned_agent_id.data or None
        if ticket.status == "Cozuldu" and ticket.resolved_at is None:
            ticket.resolved_at = datetime.utcnow()
        db.session.commit()
        flash(f"#{ticket.id} numarali talep guncellendi.", "success")
    else:
        flash("Guncelleme basarisiz, lutfen formu kontrol edin.", "danger")

    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))
