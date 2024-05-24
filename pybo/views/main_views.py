from flask import Flask, Blueprint, render_template
import requests
from bs4 import BeautifulSoup
import json

bp = Blueprint("main", __name__, url_prefix="/")

# 뉴스 업로드 시간만 추출해주는 함수(최근 4개)
# 셀렉터로 업로드 시간만 추출하기 힘듬 (기사별로 위치가 달라서)
def get_times(news_times):
  times = []
  i = 0
  cnt = 0

  while True:
    if news_times[i].text[-1] == '전':
      times.append(news_times[i].text)
      cnt += 1
    i += 1
    if cnt == 4:
      break

  return times

# 뉴스 최근 4개 정보 추출해주는 함수
def get_new_data(data, attr):
  new_data = []

  for i in range(4):
    if attr:
      new_data.append(data[i][attr])
    else:
      new_data.append(data[i].text)

  return new_data

def get_news():
  r = requests.get('https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query=%EC%BD%94%EB%A1%9C%EB%82%98')
  soup = BeautifulSoup(r.content, 'html.parser')

  news_titles = soup.select('.news_contents > .news_tit')
  news_titles = get_new_data(news_titles, '')
  news_contents = soup.select('.dsc_wrap > .dsc_txt_wrap')
  news_contents = get_new_data(news_contents, '')
  news_times = soup.select('.info_group > .info')
  news_times = get_times(news_times)
  news_thumbs = soup.select('.dsc_thumb > .thumb')
  news_thumbs = get_new_data(news_thumbs, 'data-lazysrc')
  news_links = soup.select('.dsc_thumb')
  news_links = get_new_data(news_links, 'href')

  news = []

  for i in range(4):
    news.append({
      'title' : news_titles[i],
      'content' : news_contents[i],
      'time' : news_times[i],
      'thumb' : news_thumbs[i],
      'href' : news_links[i]
    })

  return news

def get_covid_data():
  API_KEY = 'JUNpM9PuTFDKEhtZXiolYgOaS7bdQBAwc'
  url = f'https://api.corona-19.kr/korea/?serviceKey={API_KEY}'

  r = requests.get(url)
  response_bytes = r.content
  response_str = response_bytes.decode('utf-8')
  response_json = json.loads(response_str)

  covid_data = {
    'totalCnt' : response_json['korea']['totalCnt'],
    'deathCnt' : response_json['korea']['deathCnt'],
    'incDec' : response_json['korea']['incDec']
  }

  return covid_data

@bp.route("/")
def index():
  news = get_news()
  covid_data = get_covid_data()

  return render_template("index.html", news=news, covid_data=covid_data)

@bp.route("/sample")
def sample():
  return render_template("sample.html")