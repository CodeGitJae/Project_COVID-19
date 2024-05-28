document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById('genderChart').getContext('2d');

    // Use the globally defined pieChartData variable
    var data = {
        labels: Object.keys(pieChartData),
        datasets: [{
            data: Object.values(pieChartData),
            backgroundColor: ['#37a3eb', '#FF6384'],
            borderWidth: 1,
            hoverBackgroundColor:['#008ae6','#ff335f'],
        }]
    };

    var options = {
        responsive: true,
        maintainAspectRatio: false,
        hover: {
            mode: 'nearest',
            intersect: true
        },
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        var label = context.label || '';
                        var value = context.raw || 0;
                        var total = context.dataset.data.reduce((sum, current) => sum + current, 0);
                        console.log(total);
                        var percentage = (value / total * 100).toFixed(1);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            },
        },
    };

    var genderChart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: options
    });
});