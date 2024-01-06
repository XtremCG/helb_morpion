if ($("#myChart").length) {
  const xValues = JSON.parse(
    document.getElementById("compt-per-day-x").getAttribute("data-values")
  );
  const yValues = JSON.parse(
    document.getElementById("compt-per-day-y").getAttribute("data-values")
  );
  const maxValue = Math.max(...yValues);

    // Doc Chart.js

  new Chart("myChart", {
    type: "bar",
    data: {
      labels: xValues,
      datasets: [
        {
          fill: false,
          lineTension: 0,
          backgroundColor: "rgba(0,0,255,1.0)",
          borderColor: "rgba(0,0,255,0.1)",
          data: yValues,
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: "Number of games per day this month",
      },
      legend: { display: false },
      scales: {
        xAxes: [
          {
            scaleLabel: {
              display: true,
              labelString: "Day",
            },
          },
        ],
        yAxes: [
          {
            scaleLabel: {
              display: true,
              labelString: "Number of games",
            },
            ticks: {
              min: 0,
              max: maxValue + 5,
            },
          },
        ],
      },
    },
  });
}