function generateColors() {
    let r = parseInt(Math.random() * (225 - 93) + 93);
    let g = parseInt(Math.random() * (225 - 93) + 93);
    let b = parseInt(Math.random() * (225 - 93) + 93);

    return `rgb(${r}, ${g}, ${b})`;
}

function revChart(labels, data) {
    const ctx = document.getElementById('rev_stats');

    let colors = [];
    for (let i = 0; i < labels.length; i++) {
        colors.push(generateColors());
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu',
                data: data,
                borderWidth: 1,
                backgroundColor: colors
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    })
}

function medUseChart(labels, data) {
    const ctx = document.getElementById('med_use_stats');

    let colors = [];
    for (let i = 0; i < labels.length; i++) {
        colors.push(generateColors());
    }

    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tần suất thuốc sử dụng trong tháng',
                data: data,
                backgroundColor: colors
            }]
        },
        options: {}
    })
}