from flask import Flask, Blueprint, render_template

bp = Blueprint("main", __name__, url_prefix="/main")

@bp.route("/")
def index():
    return render_template("base.html")