from flask import Flask, Blueprint, render_template
import pandas as pd
import os

app = Flask(__name__)
bp = Blueprint("world", __name__, url_prefix="/world")

@bp.route("/worldmap")
def worldmap():
    return render_template("world_map.html")