import requests
import json


url = 'http://apis.data.go.kr/1352000/ODMS_COVID_04/callCovid04Api'
serviceKey = '7I86+kwZRg7drfjl1VYsPjf87SUYpH9C8qiinq4yGhtdvzKDP26bRezIP/KNbTkTeKerSADF3S0Pxsllv9lS4w=='

params ={
  'serviceKey' : serviceKey, 
  'pageNo' : '1', 
  'numOfRows' : '500', 
  'apiType' : 'JSON', 
  'std_day' : '2021-12-15', 
  'gubun' : '서울' 
  }

response = requests.get(url, params=params)
response_bytes = response.content
response_str = response_bytes.decode('utf-8')
response_json = json.loads(response_str)

# api서버에서 받아온 코로나 현황 데이터
response_data = response_json['items'][0]

print(type(response_json))