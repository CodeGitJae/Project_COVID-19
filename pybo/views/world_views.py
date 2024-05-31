from flask import Flask, Blueprint, render_template
from folium.plugins import MarkerCluster
import pandas as pd
import numpy as np
import folium
import json


bp = Blueprint("world", __name__, url_prefix="/world")

# 전세계 코로나현황.CSV 데이터 로드
wd = pd.read_csv('pybo/static/world_data/WHO_COVID19_globaldata.csv', encoding='cp949')
wd.rename(columns={"Date_reported":"날짜", "Country_code":"국가코드", "Country":"국가명","WHO_region":"지역명",
                   "New_cases":"신규확진자(명)","Cumulative_cases":"누적확진자(명)",
                   "New_deaths":"신규사망자(명)","Cumulative_deaths":"누적사망자(명)"}, inplace=True)
wd1 = wd.drop_duplicates(["국가명"],keep="last")
# wd1.drop(wd1.columns[ [4,6,8] ], axis="columns", inplace=True)
# 국가코드 오류 수정
wd1.loc[wd1['국가명']=='Namibia','국가코드'] = 'NA'


# 국가별 수도 좌표.CSV 데이터 로드
mak = pd.read_csv('pybo/static/world_data/worldcities.csv', encoding='cp949')
mak.rename(columns={"country":"국가명","city":"도시", "lat":"위도","lng":"경도", "iso":"국가코드","capital":"캐피탈"}, inplace=True)
mak1 = mak[mak['캐피탈'].isin(['primary'])]
mak1 = mak1.drop_duplicates(["국가명"],keep="last")

# 국가별 데이터 출력
def country(wd1, country_list):
    country_data_list=[]
    for country in country_list:
        country_wd = wd1[wd1["국가명"] == country]
        country_data_list.append(country_wd)

    return country_data_list


# 누적 확진자 및 사망자 값 함수                   
def covid_import_data(wd1, country, country_code):
    cases = None
    deaths = None
    # 데이터 프레임에서 값을 가져옴
    if isinstance(wd1, pd.DataFrame):
        for idx, row in wd1.iterrows():
            if row["국가명"] == country and row["국가코드"] == country_code:
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

    # 지도생성
    m = folium.Map(location=[34, 120], zoom_start=3,max_bounds=True, min_zoom=1, max_zoom=10)
    cluster = MarkerCluster().add_to(m)

    # GeoJSON 파일경로
    world_file_path = 'pybo/static/world_data/World_Countries.geojson'
    # GeoJSON 파일 읽기
    with open(world_file_path, 'rt', encoding='utf-8') as f:
        world_geo_data = json.load(f)
    # GeoJSON 데이터 추가
    folium.GeoJson(world_geo_data).add_to(m)


    # GeoJSON 데이터와 결과 데이터 병합
    result = []
    for feature in world_geo_data['features']:
        country = feature['properties']['COUNTRY']
        country_code = feature['properties']['ISO']
        cases, deaths = covid_import_data(wd1, country, country_code)

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

        result.append({"국가명": country, "국가코드": country_code, "누적확진자(명)": cases, "누적사망자(명)": deaths, "위도": latitude, "경도": longitude})

    # Choropleth 매핑 설정
    folium.Choropleth(
        geo_data=world_geo_data,
        name='choropleth',
        data=wd1,  # 국가별 확진자 수 데이터프레임
        columns=['국가코드', '누적확진자(명)'],
        key_on='feature.properties.ISO',
        highlight=True,
        fill_color='YlGnBu',  # 확진자 수에 따라 색상을 지정할 수 있음
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='누적확진자(명)'
    ).add_to(m)

    # 지도에 추가된 레이어들을 제어할 수 있는 컨트롤 추가
    folium.LayerControl().add_to(m)

    # Folium 지도를 HTML 파일로 저장
    m.save('covid19_world_map.html')


    # 마커 추가
    for idx in result:
        row = mak1[mak1['국가코드'] == idx['국가코드']]
        if not row.empty:
            latitude = row.iloc[0]["위도"]
            longitude = row.iloc[0]["경도"]
            iframe = folium.IFrame(f'{idx["국가명"]} <br>확진자: {idx["누적확진자(명)"]}<br>사망자: {idx["누적사망자(명)"]}')
            popup = folium.Popup(iframe, min_width=150, max_width=200)
            folium.Marker(
                location=[latitude, longitude],
                popup=popup,
                tooltip="Click"
            ).add_to(cluster)

    map_html = m._repr_html_()
    return render_template("covid19_world.html", map=map_html)

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
    




