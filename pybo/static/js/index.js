const API_KEY = 'JUNpM9PuTFDKEhtZXiolYgOaS7bdQBAwc'
const url = `https://api.corona-19.kr/korea/?serviceKey=${API_KEY}`
const vaccine_url = `https://api.corona-19.kr/korea/vaccine/?serviceKey=${API_KEY}`

$(document).ready(() => {
  // 코로나 확진 현황 요청 api
  $.get(url, function(response) {
    $('.totalCnt').text(response.korea.totalCnt.toLocaleString("ko-KR"))
    $('.incDec').text(response.korea.incDec.toLocaleString("ko-KR"))
    $('.deathCnt').text(response.korea.deathCnt.toLocaleString("ko-KR"))
  }).fail(function() {
    console.error('코로나 현황 요청 실패');
  });

  // 코로나 백신접종 현황 요청 api
  $.get(vaccine_url, function(response) {
    const vaccine1 = response.korea.vaccine_1
    const vaccine2 = response.korea.vaccine_2
    
    $('.vaccine1-new').text(vaccine1.vaccine_1_new);
    $('.vaccine1-all').text(vaccine1.vaccine_1.toLocaleString("ko-KR"));
    $('.vaccine1-pcnt').text(vaccine1.vaccine_1_pcnt + '%');

    $('.vaccine2-new').text(vaccine2.vaccine_2_new);
    $('.vaccine2-all').text(vaccine2.vaccine_2.toLocaleString("ko-KR"));
    $('.vaccine2-pcnt').text(vaccine2.vaccine_2_pcnt + '%');
  }).fail(function() {
    console.error('백신접종현황 요청 실패');
  });
  
  $('.carousel-item').eq(0).addClass('active');

  $('.covid-search').on('click', (e)=> { 
    e.preventDefault();
    alert('준비중 입니다.');
  })
})