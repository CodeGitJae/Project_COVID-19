from flask import Flask, Blueprint, render_template
from folium.plugins import MarkerCluster
import pandas as pd
import numpy as np
import folium.map
import json


bp = Blueprint("world", __name__, url_prefix="/world")

# CSV 데이터 로드
wd = pd.read_csv('pybo/static/world_data/WHO_COVID19_globaldata.csv', encoding='cp949')
wd.rename(columns={"Date_reported":"날짜", "Country_code":"국가코드", "Country":"국가명","WHO_region":"지역명",
                   "New_cases":"신규확진자(명)","Cumulative_cases":"누적확진자(명)",
                   "New_deaths":"신규사망자(명)","Cumulative_deaths":"누적사망자(명)"}, inplace=True)


# 국가별 데이터 출력
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

    # 데이터 프레임에서 값을 가져옴
    if isinstance(wd, pd.DataFrame):
        for idx, row in wd.iterrows():
            if row["국가명"] == country and row["지역명"] == region:
                cases = row["누적확진자(명)"]
                deaths = row["누적사망자(명)"]
                break
    else:
        print("Error: DataGrame이 아닙니다")

    return cases, deaths


##########################################################################



# 지도 생성 작업
@bp.route("/covid19_world")
def covid19_world():
    #geojson 파일경로
    world_file_path = 'pybo/static/world_data/World_Countries.geojson'

    # geojson 파일 읽기
    with open(world_file_path, 'rt', encoding='utf-8') as f:
        world_geo_data = json.load(f)


    # GeoJSON 데이터와 결과 데이터 병합
    result = []
    for feature in world_geo_data['features']:
        country = feature['properties'].get('COUNTRY', '')
        region = feature['properties'].get('COUNTRYAFF', '')
        cases, deaths = covid_import_data(wd, country, region)

        # GeoJSON에서 위도와 경도 가져오기
        coordinates = feature['geometry']['coordinates']
        if feature['geometry']['type'] == 'Polygon':
            # 폴리곤의 첫 번째 좌표를 사용
            longitude, latitude = coordinates[0][0]
        elif feature['geometry']['type'] == 'MultiPolygon':
            # 첫 번째 폴리곤의 첫 번째 좌표를 사용
            longitude, latitude = coordinates[0][0][0]
        else:
            continue  # 다른 유형의 지오메트리는 건너뜀

        result.append({"COUNTRY": country, "COUNTRYAFF": region, "누적확진자(명)": cases, "누적사망자(명)": deaths, "위도": latitude, "경도": longitude})


    # 지도생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=3)
    cluster = MarkerCluster().add_to(m)

    # geojson 데이터 로드
    folium.GeoJson(world_geo_data).add_to(m)


    # Choropleth 매핑 설정
    data_dict = {idx['COUNTRY']: idx['누적확진자(명)'] for idx in result if idx['누적확진자(명)'] is not None}
    folium.Choropleth(
        geo_data=world_geo_data,
        name='choropleth',
        data=pd.DataFrame.from_dict(data_dict, orient='index').reset_index(),
        columns=["index", 0],
        key_on="feature.properties.COUNTRY",
        fill_color="YlGnBu"
    ).add_to(m)

    # 마커 추가
    for idx in result:
        latitude = idx["위도"]
        longitude = idx["경도"]

        if latitude and longitude:
            iframe = folium.Iframe(f'{idx["COUNTRY"]} {idx["COUNTRYAFF"]} <br>확진자: {idx["누적확진자(명)"]}<br>사망자: {idx["누적사망자(명)"]}')
            popup = folium.Popup(iframe, min_width=150, max_width=200)
            folium.Marker(
                location=[latitude, longitude],
                popup=popup,
                tooltip="Click"
            ).add_to(cluster)


        map = m._repr_html_()

        return render_template("world/covid19_world.html", map=map)