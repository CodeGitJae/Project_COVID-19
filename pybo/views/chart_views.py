from flask import Flask, Blueprint, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)
bp = Blueprint("chart", __name__, url_prefix="/chart")

# 엑셀 파일 읽어오기
cov_data = pd.read_excel(os.path.join("pybo", "static", "chart_xlsx", "cov_data.xlsx"))

@bp.route("/age_chart")
def age_chart():
    return render_template("age_chart.html", data=cov_data.to_dict())

@bp.route("/age_data")
def age_data():
    return jsonify(cov_data.to_dict())
