from flask import Flask, Blueprint, jsonify, render_template
from folium.plugins import MarkerCluster
import pandas as pd
import numpy as np
import folium.map
import json


bp = Blueprint("world", __name__, url_prefix="/world")

# Load CSV data
wd = pd.read_csv('pybo/static/world_data/WHO_COVID19_globaldata.csv', encoding='cp949')
wd.rename(columns={"Date_reported":"날짜", "Country_code":"국가코드", "Country":"국가명","WHO_region":"지역명",
                   "New_cases":"신규확진자(명)","Cumulative_cases":"누적확진자(명)",
                   "New_deaths":"신규사망자(명)","Cumulative_deaths":"누적사망자(명)"}, inplace=True)


# 국가별 기준으로 나누어 출력함
def country(wd, country_list):
    country_data_list=[]

    for country in country_list:
        country_wd = wd[wd["국가명"] == country]
        country_data_list.append(country_wd)

    return country_data_list


# 누적 확진자 및 사망자 값 함수
def covid_import_data(wd, country, region):
    cases = None
    deaths = None

    # 데이터 프레임인 값만 가져다 쓰도록 설정
    if isinstance(wd, pd.DataFrame):
        for idx, row in wd.iterrows():
            if row["국가명"] == country and row["지역명"] == region:
                cases = row["누적확진자(명)"]
                deaths = row["누적사망자(명)"]
                break
    else:
        print("Error: wd1 is not a DataGrame")

    return cases, deaths


##########################################################################




# MAP작업
@bp.route("/covid19_world")
def covid19_world():
    #geojson 파일경로
    world_file_path = 'pybo/static/world_data/World_Countries.geojson'

    # geojson 파일 읽기
    with open(world_file_path, 'rt', encoding='utf-8') as f:
        world_geo_data = json.load(f)

    # GeoJSON 데이터와 result 데이터 병합
    result = []
    # GeoJSON 데이터의 features를 순회하며 처리
    for feature in world_geo_data['features']:
        country = feature['properties']['COUNTRY']
        region = feature['properties']['COUNTRYAFF']
        cases, deaths = covid_import_data(wd, country, region)
        result.append({"COUNTRY":country, "COUNTRYAFF":region, "누적확진자(명)": cases, "누적사망자(명)": deaths})


    # 지도생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=3)
    cluster = MarkerCluster().add_to(m)

    # geojson 데이터 로드

    folium.GeoJson(world_geo_data).add_to(m)


    # GeoJSON 데이터와 result 데이터 병합
    for feature in world_geo_data['features']:
        if 'name' in  feature['properties']:
            for idx in result:
                if idx['COUNTRY'] in feature['properties']['COUNTRY']:
                    feature['properties']['COUNTRY'] = idx['COUNTRY']

    
    data_dict = {idx['COUNTRY'] : idx['누적확진자(명)'] for idx in result}
    folium.Choropleth(
        wgeo_data= world_geo_data,
        name='chorpleth',
        data=data_dict,
        columns=["COUNTRY","확진자"],
        key_on="features.properties.COUNTRY",
        fill_color="YLGnBu"
    ).add_to(m)

    # 마커추가
    for idx in result:
        latitude = idx["위도"]
        longitude = idx["경도"]

        iframe = folium.Iframe(f'{idx["국가명"]} {idx["지역명"]} <br>확진자: {idx["누적확진자(명)"]}<br>사망자: {idx["누적사망자(명)"]}')
        popup = folium.Popup(iframe, min_width=150, max_width=200)
        folium.Marker(
            location=[latitude, longitude],
            popup=popup,
            tooltip="Click"
        ).add_to(cluster)


        map = m._repr_html_()

        return render_template("world/covid19_world.html", map=map)




##############################################################################



#@bp.route("/world_data")
#def world_data():
#    return jsonify(world_data.to_dict(orient="records"))
#
#@bp.route("/world_geojson")
#def world_geojson():
#    # GeoJSON 데이터를 각 국가에 대한 데이터와 일치시킵니다.
#    geojson_features = geojson_data['FeatureCollection']#
#
#    for feature in geojson_features:
#        country_name = feature['properties']['name']
#        country_data = world_data[world_data['Country'] == country_name]
#
#        if not country_data.empty:
#            feature['properties']['new_cases'] = int(country_data['New_cases'].iloc[-1])
#            feature['properties']['cumulative_cases'] = int(country_data['Cumulative_cases'].iloc[-1])
#            feature['properties']['new_deaths'] = int(country_data['New_deaths'].iloc[-1])
#            feature['properties']['cumulative_deaths'] = int(country_data['Cumulative_deaths'].iloc[-1])
#        else:
#            feature['properties']['new_cases'] = 0
#            feature['properties']['cumulative_cases'] = 0
#            feature['properties']['new_deaths'] = 0
#            feature['properties']['cumulative_deaths'] = 0
#    return jsonify(geojson_data)
#
#if __name__ == "__main__":
#    app.run(debug=True)
