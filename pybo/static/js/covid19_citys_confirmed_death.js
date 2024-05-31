document.addEventListener("DOMContentLoaded", function(){
    const ctx = document.getElementById('SouthKoreaChartofCitys').getContext('2d');
   
    function getRandomColor(){
        var letters = '0123456789ABCDEF';
        var color ="#";
        for (var i = 0; i<6; i++){
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    // 확진자, 사망자 데이터 객체를 생성하는 함수
    function getChartData(data){
        let datasets = {};

        Object.keys(data).forEach( city =>{
            // 확진자 데이터 세트 객체 생성
            if(city !== '일자'){
                datasets[city] ={
                    label: city,
                    data: [],
                    borderColor: getRandomColor(),
                    type:'line'
                }
                Object.values(data[city]).forEach(value =>{
                    datasets[city].data.push(value);
                });
            }
        });
        // 저장한 각각의 객체를 반환 (labels는 고정값)
        return {
            labels: Object.values(data.일자),
            datasets: Object.values(datasets)
        };
    }

    //초기 데이터는 확진자 데이터를 사용하여 차트를 설정
    let charData = getChartData(lineforConfirmed);

    // Config Block
    const config = {
        type: 'line',
        data: charData,
        options: {
            responsive: true,          // CSS 부모 컨테이너에 따라 자동으로 크기를 조정
            maintainAspectRatio: false,    // 차트 가로 세로 비율을 부모의 요소 크기에 맞게 조정
            elements:{
                point:{
                    radius: 1,   // 동그란 포인트 반지름을 0으로 설정 (포인트 비활성)
                }
            },
            scales:{
                y:{
                    beginAtZero: true
                }
            },
            plugins:{
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'xy',
                        threshold: 10
                    },
                    zoom: {
                        wheel: {
                            enabled: true
                        }
                    }
                }                
            }
        }
    };

    // Render Block  
    var SouthKoreaChartofCitys = new Chart(ctx, config);

    // click event
    document.getElementById('confirmedBtn').addEventListener('click', function() {
        chartData = getChartData(lineforConfirmed);
        SouthKoreaChartofCitys.data = chartData;
        SouthKoreaChartofCitys.update();
    });

    document.getElementById('deathBtn').addEventListener('click', function() {
        chartData = getChartData(lineforDeath);
        SouthKoreaChartofCitys.data = chartData;
        SouthKoreaChartofCitys.update();
    });

    document.getElementById('resetBtn').addEventListener('click', function(){
        SouthKoreaChartofCitys.resetZoom();
    });

});


