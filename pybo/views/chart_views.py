from flask import Flask, Blueprint, render_template, jsonify
import pandas as pd
import os
from pybo.data_processing import get_gender_data, get_confirmed_data, get_death_data

app = Flask(__name__)
bp = Blueprint("chart", __name__, url_prefix="/chart")

# line chart 데이터 전송용 라우터
@bp.route("/totalSouthKoreaChartOfCitys")
def total_inkorea_chart():
    confirmed_raw_data = get_confirmed_data().to_dict()
    death_raw_data = get_death_data().to_dict()
    
    return render_template("inkorea/covid19_citys_confirmed_death.html", confirmedCase=confirmed_raw_data, deathCase=death_raw_data)


## pie chart 데이터 전송용 라우터 
@bp.route("/gender_each_chart")
def gender_chart():
    pie_chart, sumTotal_gender = get_gender_data()

    return render_template("inkorea/gender_pie_chart.html", pie_chart=pie_chart, sumTotal_gender=sumTotal_gender)

# 엑셀 파일 읽어오기
cov_data = pd.read_excel(os.path.join("pybo", "static", "chart_xlsx", "cov_data.xlsx"))

@bp.route("/age_chart")
def age_chart():
    return render_template("age_chart.html", data=cov_data.to_dict())

@bp.route("/age_data")
def age_data():
    return jsonify(cov_data.to_dict())
