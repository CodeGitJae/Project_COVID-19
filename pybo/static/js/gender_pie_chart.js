document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById('genderChart').getContext('2d');

    var data = {
        labels: Object.keys(pieChartData),
        datasets: [{
            data: Object.values(pieChartData),
            backgroundColor: ['#37a3eb', '#FF6384'],
            borderWidth: 1,
            hoverOffset: 50,
            hoverBackgroundColor:['#008ae6','#ff335f'],
        }]
    };
    console.log(data)
    var options = {
        responsive: true,                // CSS 부모 컨테이너에 따라 자동으로 크기를 조정
        maintainAspectRatio: false,      // 차트 가로 세로 비율을 부모의 요소 크기에 맞게 조정
        layout:{
            padding:{
                bottom: 15
            },
        },
        plugins: {
            legend: {
                position: 'top',
            },
            datalabels:{
                align: 'center',
                color: '#ffffff',   // 흰색글자
                font: {
                    size: 35,  //글자 크기 16px
                    weight: 'bold'   // 글자 굵기를 볼드체로 설정
                },
                formatter: (value, context) =>{
                    //console.log(value)
                    //console.log(context)
                    //console.log(context.chart.data.datasets[0].data);
                    const datapoints = context.chart.data.datasets[0].data;
                    const genderLabels = context.chart.data.labels;
                    function totalSum(total, datapoint){
                        return total + datapoint;
                    }
                    const totalValue = datapoints.reduce(totalSum, 0);
                    const percentageValue = (value / totalValue * 100).toFixed(1);
                    
                    // 현재 데이터 포인트의 인덱스 가져오기
                    const dataIndex = context.dataIndex;
                    // genderLabels 배열에서 현재 인덱스에 해당하는 라벨 가져오기
                    const genderLabel = genderLabels[dataIndex];

                    return `${genderLabel}: (${percentageValue}%)`;
                }
            },
            tooltip: {                      
                enabled: false,   // formatter 데이터 살리기 위해서 툹팁 비활성화
                callbacks: {                             
                    label: function(context) {
                        var label = context.label || '';
                        var value = context.raw || 0;         // 주석 처리한 3줄은 퍼센트 데이터까지 모두 표현하고 싶은 경우
                        // var total = context.dataset.data.reduce((sum, current) => sum + current, 0);  
                        // var percentage = (value / total * 100).toFixed(1);          
                        //return `${label}: ${value} (${percentage}%)`;
                        var formattedValue = value.toLocaleString();
                        return `${label}: ${formattedValue}명`;
                    }
                }
            },
        },
    };

    var genderChart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: options,
        plugins: [ChartDataLabels]
    });
});