from flask import Flask, Blueprint, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)
bp = Blueprint("chart", __name__, url_prefix="/chart")

gender_df = pd.read_excel('pybo\static\others\코로나19 확진자 발생현황.xlsx', sheet_name=3, skiprows=3, header=1)
gender_df.drop([0], axis="index", inplace=True)
gender_df.replace("-", 0, inplace=True)
gender_df.rename(columns={"남성(명)":"남자","여성(명)": "여자"}, inplace=True)
gender_df["연도"]= gender_df["일자"].dt.year
gender_df["월"]= gender_df["일자"].dt.month


@bp.route("/gender_each_chart")
def gender_chart():
    
    total_pivot_df = pd.pivot_table(gender_df, values=["남자", "여자"], index="연도", aggfunc="sum", margins=True, margins_name="전체")
    pie_chart= total_pivot_df.loc["전체"].to_dict()

    total_pivot_df.drop(total_pivot_df.index[:4], inplace=True)
    total_pivot_df['총 확진자'] = total_pivot_df.sum(axis=1)
    total_pivot_df['총 확진자']['전체'] = "{:,}".format(total_pivot_df['총 확진자']['전체'])
    total_pivot_df['남자']['전체'] = "{:,}".format(total_pivot_df['남자']['전체'])
    total_pivot_df['여자']['전체'] = "{:,}".format(total_pivot_df['여자']['전체'])
    sumTotal_gender = total_pivot_df.to_dict()

    return render_template("inkorea/gender_pie_chart.html", pie_chart=pie_chart, sumTotal_gender=sumTotal_gender)

# 엑셀 파일 읽어오기
cov_data = pd.read_excel(os.path.join("pybo", "static", "chart_xlsx", "cov_data.xlsx"))

@bp.route("/age_chart")
def age_chart():
    return render_template("age_chart.html", data=cov_data.to_dict())

@bp.route("/age_data")
def age_data():
    return jsonify(cov_data.to_dict())
