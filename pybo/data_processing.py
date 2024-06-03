import pandas as pd
from datetime import datetime
import numpy as np
import os

##  pandas로 가공한 데이터 위한 함수 (데이터 프레임)
def load_data_second ():
    ## raw 데이타 path 설정 시작
    data_path= os.path.join("pybo", "static", "chart_xlsx", "코로나19 확진자 발생현황.xlsx")

    ## 전국 시도별 코로나 19 확진자 데이터 로드 및 가공 
    covid19_city_confirmed= pd.read_excel(data_path, sheet_name=4, skiprows=3, header=1)
    covid19_city_confirmed.drop([0], axis="index", inplace=True)
    covid19_city_confirmed.drop(covid19_city_confirmed.columns[[1,-1]], axis=1, inplace=True)
    covid19_city_confirmed.replace("-", 0, inplace=True)
    # covid19_city_confirmed["일자"] = pd.to_datetime(covid19_city_confirmed["일자"])
    covid19_city_confirmed["일자"]= covid19_city_confirmed["일자"].apply(lambda x : datetime.strftime(x, '%Y/%m/%d'))


    ## 전국 시도별 코로나 19 사망자 데이터 로드 및 가공 
    covid19_city_death= pd.read_excel(data_path, sheet_name=5, skiprows=3, header=1)
    covid19_city_death.drop([0], axis="index", inplace=True)
    covid19_city_death.drop(covid19_city_death.columns[[1,-1]], axis=1, inplace=True)
    # covid19_city_death["일자"] = pd.to_datetime(covid19_city_death["일자"])
    covid19_city_death["일자"]= covid19_city_death["일자"].apply(lambda x : datetime.strftime(x, '%Y/%m/%d'))


    ## 성별(남/여) 확진환자 데이터 로드 및 가공 
    gender_df = pd.read_excel(data_path, sheet_name=3, skiprows=3, header=1)
    gender_df.drop([0], axis="index", inplace=True)
    gender_df.replace("-", 0, inplace=True)
    gender_df.rename(columns={"남성(명)":"남자","여성(명)": "여자"}, inplace=True)
    gender_df["일자"] = pd.to_datetime(gender_df["일자"])
    gender_df["연도"]= gender_df["일자"].dt.year

    return covid19_city_confirmed, covid19_city_death, gender_df

    ## chart_views.py // 시도별 확진자 데이터
def get_confirmed_data():
    covid19_city_confirmed, _, _ = load_data_second()
    return  covid19_city_confirmed

    ## chart_views.py // 시도별 사망자 데이터
def get_death_data():
    _, covid19_city_death, _ = load_data_second()
    return covid19_city_death

    ## chart_views.py // 국내 성별 확진자 데이터
def get_gender_data():
    _, _, gender_df = load_data_second()

    total_pivot_df = pd.pivot_table(gender_df, values=["남자", "여자"], index="연도", aggfunc="sum", margins=True, margins_name="전체")
    pie_chart= total_pivot_df.loc["전체"].to_dict()

    total_pivot_df.drop(total_pivot_df.index[:4], inplace=True)
    total_pivot_df['총 확진자'] = total_pivot_df.sum(axis=1)
    total_pivot_df['총 확진자']['전체'] = "{:,}".format(total_pivot_df['총 확진자']['전체'])     ## 숫자 단위에 따라 콤마( , ) 적용 [전체/남자/여자]
    total_pivot_df['남자']['전체'] = "{:,}".format(total_pivot_df['남자']['전체'])              
    total_pivot_df['여자']['전체'] = "{:,}".format(total_pivot_df['여자']['전체'])              
    sumTotal_gender = total_pivot_df.to_dict()

    return pie_chart, sumTotal_gender

###########################################################################

## citygungu_view.py // 위경도 + 전국 시도명, 시군구별 데이터 가공
def load_data_first():

    ## raw 데이터 path 설정 시작
    covid19_public_data_path= os.path.join("pybo", "static", "chart_xlsx", "코로나19 확진자 발생현황.xlsx")
    korea_lat_lon_data_path = os.path.join("pybo", "static", "others", "korea_latitude_longitude.csv")

    ## 전국 시군구 위도 데이터 가공##
    df= pd.read_csv(korea_lat_lon_data_path, encoding="cp949")
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

        ##  국내 시군구 코로나 발생현황 데이터 가공 ##
            ##   두 데이터 프레임 Merge 진행 ##
    df = pd.read_excel(covid19_public_data_path, sheet_name=6, skiprows=6)
    df1 = df.copy()
    df1.drop(0, axis=0, inplace=True)
    df1.replace("-", 0, inplace=True)

    df1 = pd.merge(df, dfn, on=["시도명","시군구"])
    filter = df1["시군구"] != "합계"
    df1 = df1[filter]
    # print(df1[df1['시도명'] == '경기'])
    
    return df1