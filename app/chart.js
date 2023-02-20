console.log("hello")


const chartData = {
    labels: ["Aanwezig", "Afwezig"],
    data: [80, 20],
}

const myChart = document.querySelector(".my-chart");

new Chart(myChart, {
    type: "doughnut",
    data: {
        labels: chartData.labels,
        datasets: [
            {
                label: "Mijn Aanwezigheid",
                data: chartData.data,
            }
        ]
    }
});
