from bs4 import BeautifulSoup
import requests

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
def get_new_data(data):
  new_data = []

  for i in range(4):
    new_data.append(data[i].text)

  return new_data

# 뉴스 최근 4개 썸네일 추출해주는 함수
def get_new_thumb(thumbs):
  new_thumbs = []

  for i in range(4):
    new_thumbs.append(thumbs[i]['data-lazysrc'])

  return new_thumbs

def get_news():
  r = requests.get('https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query=%EC%BD%94%EB%A1%9C%EB%82%98')
  soup = BeautifulSoup(r.content, 'html.parser')

  news_titles = soup.select('.news_contents > .news_tit')
  news_titles = get_new_data(news_titles)
  news_contents = soup.select('.dsc_wrap > .dsc_txt_wrap')
  news_contents = get_new_data(news_contents)
  news_times = soup.select('.info_group > .info')
  news_times = get_times(news_times)
  news_thumbs = soup.select('.dsc_thumb > .thumb')
  news_thumbs = get_new_thumb(news_thumbs)
  news_links = soup.select('.dsc_thumb')

  for i in range(4):
    print(news_links[i]['href'])

  # news = []

  # for i in range(4):
  #   news.append({
  #     'title' : news_titles[i],
  #     'content' : news_contents[i],
  #     'time' : news_times[i],
  #     'thumb' : news_thumbs[i]
  #   })

  # return news

get_news()