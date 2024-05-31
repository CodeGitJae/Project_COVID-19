from flask import Flask, Blueprint, render_template,request, redirect, url_for
import folium
import json
import folium.map
import pandas as pd
import os
from folium.plugins import MarkerCluster
from pybo.data_processing import load_data_first

bp = Blueprint("citygungu", __name__, url_prefix="/citygungu")

## 데이터 path 설정 시작
korea_geoData_path = os.path.join("pybo", "static", "others", "korea-geoData.json")
covid19_img_path = os.path.join("pybo", "static", "others", "covid19img.png")

## data_processing.py 함수 선언
df1 = load_data_first()

    ## 각 시도명 기준으로 나누어 출력하는 함수 ##
def citys(df, city_list):
    city_data_list= []

    for city in city_list:
        city_df = df[df1["시도명"]== city]
        city_data_list.append(city_df)
    
    return city_data_list

    ##  누적확진자, 누적 사망자 값 가져오는 함수 ##
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

    ## 아래 부터 라우터 및 map 작업 ##
    
    ## 두번쨰 라우터
@bp.route("/covid19_inkorea/<selected_city>")
def covid19_inkorea_city(selected_city):

    if selected_city == 'all':
        return redirect(url_for('citygungu.covid19_inkorea'))

    city_list_all = ["서울", "부산", "대구", "인천", "광주",
        "대전", "울산", "세종", "경기", "강원",
        "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
    
    city_list = [selected_city]

    korea_city = citys(df1, city_list)
    lat = 0
    lon = 0

    result = []
    for city_df in korea_city:
        for idx, row in city_df.iterrows():
            city = row["시도명"]
            gungu = row["시군구"]
            latitude = row["위도"]
            longitude = row["경도"]
            cofirme, death = make_import_data(df1, city, gungu)
            result.append({"시도명": city, "시군구": gungu, "확진자": cofirme, "사망자": death, "위도": latitude, "경도": longitude})
            lat =latitude
            lon = longitude
    ###  map 작업  ###   
    
    m = folium.Map(location=[lat, lon], zoom_start=9)
    cluster = MarkerCluster().add_to(m)

    with open(korea_geoData_path, 'rt', encoding='utf-8') as f:

        geoJson_data = json.load(f)
    folium.GeoJson(geoJson_data).add_to(m)

    ## 중복된 지역에 대한 code추출 --- start

    # 시군구 중복되는 code값을 추출
    # 중복된 값을 가지는 key-value 쌍을 저장할 딕셔너리 생성
    arr = dict()

    # geoJson에 code와 name을 추출해서 arr에 저장
    for feature in geoJson_data['features']:
        code = feature['properties']['code']
        arr[code] = feature['properties']['name']

    # 중복된 값을 가진 value를 저장할 딕셔너리
    duplicate_values = {}

    # 딕셔너리를 순회하면서 중복된 값을 가진 key를 저장
    for key, value in arr.items():
        if value in duplicate_values:
            if key not in duplicate_values[value]:
                duplicate_values[value].append(key)
        else:
            duplicate_values[value] = [key]

    # 정확히 일치하는 중복된 값의 key 추출
    exact_duplicate_pairs = []
    print(duplicate_values)
    for value, keys in duplicate_values.items():
      if len(keys) > 1 and len(set(arr[key] for key in keys)) == 1:
          exact_duplicate_pairs.append((value, keys))
          
    dup_city = []
    #print("정확히 일치하는 중복된 값의 value와 keys:")
    for value, keys in exact_duplicate_pairs:
        #print(f"{value} : {keys}")
        dup_city.append(value)

    # 작업해보니 code는 추출할 필요가 없었음
    ## 중복된 지역에 대한 code추출 --- end

    # result에 중복된 시군구는 '시도명 시군구'로 처리
    for value, keys in exact_duplicate_pairs:
        for data in result:
            if value == data['시군구']:
                data['시군구'] = data['시도명'] + ' ' + data['시군구']

    # geoJson에 중복된 시군구는 '시도명 시군구'로 처리
    # 시도명에 공백 기준으로 앞에 지역만 추출해서 시군구에 연결함
    for feature in geoJson_data['features']:    # geojson과 위경도 name값 매칭을 위한 for문
       if feature['properties']['name'] in dup_city:
          if feature['id'].find(' ') != -1:
            feature['properties']['name'] = feature['id'][:feature['id'].find(' ')] + ' ' + feature['properties']['name']
          else:
            feature['properties']['name'] = feature['id'] + ' ' + feature['properties']['name']  
          #print(feature['properties']['name'])

    for r in result:
        if r['시군구'] == '세종':
            r['시군구']='세종시'

    data_dict = {entry['시군구'] : entry['확진자'] for entry in result}
    folium.Choropleth(
        geo_data=geoJson_data,
        name='chorpleth',
        data = data_dict,
        columns=["시군구","확진자"],
        key_on="properties.name",
        fill_color="Spectral_r"
    ).add_to(m)

    for entry in result:
        latitude = entry["위도"]
        longitude = entry["경도"]

        iframe = folium.IFrame(f'{entry["시도명"]} {entry["시군구"]} <br>확진자: {entry["확진자"]}<br>사망자: {entry["사망자"]}')
        popup = folium.Popup(iframe, min_width=170, max_width=200)
        folium.Marker(
            location=[latitude, longitude],
            icon=folium.CustomIcon(icon_size=(20,20), icon_anchor=(5,5), icon_image=covid19_img_path),
            popup=popup,
            tooltip="Please Click"
        ).add_to(cluster)

    part_map = m._repr_html_()
    
    return render_template("inkorea/covid19_inkorea.html", map= part_map, city_list=city_list_all, result=result, selected_city=selected_city)


## 첫번째 라우터 시작

@bp.route("/covid19_inkorea")
def covid19_inkorea():
    global df1

    city_list = ["서울", "부산", "대구", "인천", "광주",
        "대전", "울산", "세종", "경기", "강원",
        "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

#   selected_city = request.args.get("selected_city")   ajax 관련 코드 사용 x
    korea_city = citys(df1, city_list)

    result = []
    for city_df in korea_city:
        for idx, row in city_df.iterrows():
            city = row["시도명"]
            gungu = row["시군구"]
            latitude = row["위도"]
            longitude = row["경도"]
            cofirme, death = make_import_data(df1, city, gungu)
#            if city == selected_city:                  ajax 관련 코드 코드 사용 x
            result.append({"시도명": city, "시군구": gungu, "확진자": cofirme, "사망자": death, "위도": latitude, "경도": longitude})
            

    ###  map 작업  ###   
    
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)
    cluster = MarkerCluster().add_to(m)

    with open(korea_geoData_path, 'rt', encoding='utf-8') as f:

        geoJson_data = json.load(f)
    folium.GeoJson(geoJson_data).add_to(m)


    for feature in geoJson_data['features']:    # geojson과 위경도 name값 매칭을 위한 for문
        if 'name' in feature['properties']:
            for entry in result:
                if entry['시군구'] in feature['properties']['name']:
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


    for entry in result:
        latitude = entry["위도"]
        longitude = entry["경도"]

        iframe = folium.IFrame(f'{entry["시도명"]} {entry["시군구"]} <br>확진자: {entry["확진자"]}<br>사망자: {entry["사망자"]}')
        popup = folium.Popup(iframe, min_width=170, max_width=200)
        folium.Marker(
            location=[latitude, longitude],
            icon=folium.CustomIcon(icon_size=(20,20), icon_anchor=(5,5), icon_image=covid19_img_path),
            popup=popup,
            tooltip="Please Click"
        ).add_to(cluster)

    map = m._repr_html_()

    return render_template("inkorea/covid19_inkorea.html", map= map, city_list=city_list, result=result)