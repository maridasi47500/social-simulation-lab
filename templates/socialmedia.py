from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint("socialmedia", __name__)


@bp.route("/socialmedia/")
def index():
    """Show all the socialmedias, most recent first."""
    db = get_db()
    socialmedias = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM socialmedia p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("socialmedia/index.html", socialmedias=socialmedias)


def get_socialmedia(id, check_author=True):
    """Get a socialmedia and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of socialmedia to get
    :param check_author: require the current user to be the author
    :return: the socialmedia with author information
    :raise 404: if a socialmedia with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    socialmedia = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM socialmedia p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if socialmedia is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and socialmedia["author_id"] != g.user["id"]:
        abort(403)

    return socialmedia


@bp.route("/socialmedia/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new socialmedia for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO socialmedia (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("socialmedia.index"))

    return render_template("socialmedia/create.html")


@bp.route("/socialmedia/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a socialmedia if the current user is the author."""
    socialmedia = get_socialmedia(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE socialmedia SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("socialmedia.index"))

    return render_template("socialmedia/update.html", socialmedia=socialmedia)


@bp.route("/socialmedia/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a socialmedia.

    Ensures that the socialmedia exists and that the logged in user is the
    author of the socialmedia.
    """
    get_socialmedia(id)
    db = get_db()
    db.execute("DELETE FROM socialmedia WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("socialmedia.index"))
