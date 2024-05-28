from flask import Flask, Blueprint, render_template,request
import folium
import json
import folium.map
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster

bp = Blueprint("citygungu", __name__, url_prefix="/citygungu")

df= pd.read_csv('pybo/static/others/korea_latitude_longitude.csv', encoding="cp949")
dfn = df.copy()
dfn.drop(["bjd_cd", "center_point", "sd_cd","sgg_cd","emd_cd","bjd_nm"], axis=1, inplace=True)
dfn.rename(columns={"center_long":"경도", "center_lati":"위도", "sd_nm":"시도명","sgg_nm":"시군구"}, inplace=True)
dfn.drop(dfn.columns[5:], axis=1, inplace=True)
sejongfilter = dfn["시도명"]=="세종특별자치시"
dfn.loc[sejongfilter, "시군구"]= dfn.loc[sejongfilter, "시군구"].replace(np.nan, "세종")
dfn.loc[sejongfilter, "level"]= dfn.loc[sejongfilter, "level"].replace(0, 1)
filter2= dfn["level"]==1
dfn = dfn[filter2]
dfn = dfn.drop_duplicates(['시도명','시군구'])
# print(dfn)

dfn["시도명"].replace({"서울특별시":"서울", "부산광역시":"부산","대구광역시":"대구",
             "인천광역시":"인천","광주광역시":"광주","대전광역시":"대전",
             "울산광역시":"울산","세종특별자치시":"세종", "경기도":"경기",
             "강원도":"강원","충청북도":"충북","충청남도":"충남","전라북도":"전북",
             "전라남도":"전남","경상북도":"경북","경상남도":"경남","제주특별자치도":"제주"}, inplace=True)

###############↑↑↑↑↑↑↑↑↑↑↑↑↑ 전국 시군구 위도 데이터 가공↑↑↑↑↑↑↑↑↑↑↑↑↑
df = pd.read_excel('pybo\static\others\코로나19 확진자 발생현황.xlsx', sheet_name=6, skiprows=6)
df1 = df.copy()
df1.drop(0, axis=0, inplace=True)
df1.replace("-", 0, inplace=True)

df1 = pd.merge(df, dfn, on=["시도명","시군구"])
filter = df1["시군구"] != "합계"
df1 = df1[filter]
# print(df1)

#################↑↑↑↑↑↑   국내 시군구 코로나 발생현황 데이터 가공 / 두 데이터 프레임 Merge 진행 ↑↑↑↑↑↑↑↑↑↑↑↑
def citys(df, city_list):
    city_data_list= []

    for city in city_list:
        city_df = df[df1["시도명"]== city]
        city_data_list.append(city_df)
    
    return city_data_list

###########↑↑↑↑↑↑↑↑↑↑↑↑ 각 시도명 기준으로 나누어 출력하는 함수  ↑↑↑↑↑↑↑↑↑↑######

def make_import_data(df1, city, gungu):
    cofirme = None
    death = None

    if isinstance(df1, pd.DataFrame):    ## 데이터 프레임인 값만 가져다 쓰도록 설정
        for idx, row in df1.iterrows():
            if row["시도명"] == city and row["시군구"] == gungu:
                cofirme = row["누적확진자(명)"]
                death = row["누적사망자(명)"]
                break
    else:
        print("Error: df1 is not a DataFrame")
    
    return cofirme, death

########################  누적확진자, 누적사망자 값 가져오는 함수 ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑




@bp.route("/covid19_inkorea/<selected_city>")
def covid19_inkorea_city(selected_city):
    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print(selected_city)
    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    city_list = [selected_city]

#   selected_city = request.args.get("selected_city")
    korea_city = citys(df1, city_list)

    result = []
    for city_df in korea_city:
        for idx, row in city_df.iterrows():
            city = row["시도명"]
            gungu = row["시군구"]
            latitude = row["위도"]
            longitude = row["경도"]
            cofirme, death = make_import_data(df1, city, gungu)
#            if city == selected_city:
            result.append({"시도명": city, "시군구": gungu, "확진자": cofirme, "사망자": death, "위도": latitude, "경도": longitude})
            
    
    return result

@bp.route("/covid19_inkorea")
def covid19_inkorea():
    global df1

    city_list = ["서울", "부산", "대구", "인천", "광주",
        "대전", "울산", "세종", "경기", "강원",
        "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

#   selected_city = request.args.get("selected_city")
    korea_city = citys(df1, city_list)

    result = []
    for city_df in korea_city:
        for idx, row in city_df.iterrows():
            city = row["시도명"]
            gungu = row["시군구"]
            latitude = row["위도"]
            longitude = row["경도"]
            cofirme, death = make_import_data(df1, city, gungu)
#            if city == selected_city:
            result.append({"시도명": city, "시군구": gungu, "확진자": cofirme, "사망자": death, "위도": latitude, "경도": longitude})
            

    ########  ↓↓↓↓↓↓↓↓↓ map 작업 ↓↓↓↓↓↓↓↓↓↓ #######   
    
    m = folium.Map(location=[36.5, 127.5], zoom_start=5)
    cluster = MarkerCluster().add_to(m)

    file_path = "pybo/static/others/korea-geoData.json"
    with open(file_path, 'rt', encoding='utf-8') as f:

        geoJson_data = json.load(f)
    folium.GeoJson(geoJson_data).add_to(m)


    for feature in geoJson_data['features']:    # geojson과 위경도 name값 매칭을 위한 for문
        if 'name' in feature['properties']:
            for entry in result:
                if entry['시군구'][:3] in feature['properties']['name'][:3]:
                    feature['properties']['name'] = entry['시군구']

    data_dict = {entry['시군구'] : entry['확진자'] for entry in result}
    folium.Choropleth(
        geo_data=geoJson_data,
        name='chorpleth',
        data = data_dict,
        columns=["시군구","확진자"],
        key_on="properties.name",
        fill_color="Spectral_r"
    ).add_to(m)

    img = 'pybo/static/others/covid19img.png'

    for entry in result:
        latitude = entry["위도"]
        longitude = entry["경도"]

        iframe = folium.IFrame(f'{entry["시도명"]} {entry["시군구"]} <br>확진자: {entry["확진자"]}<br>사망자: {entry["사망자"]}')
        popup = folium.Popup(iframe, min_width=170, max_width=200)
        folium.Marker(
            location=[latitude, longitude],
            icon=folium.CustomIcon(icon_size=(20,20), icon_anchor=(5,5), icon_image=img),
            popup=popup,
            tooltip="Please Click"
        ).add_to(cluster)

    map = m._repr_html_()

    return render_template("inkorea/covid19_inkorea.html", map= map, city_list=city_list, result=result)