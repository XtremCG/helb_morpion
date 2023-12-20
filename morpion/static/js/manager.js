if ($("#myChart").length) {
  const xValues = JSON.parse(
    document.getElementById("compteur-par-jour-x").getAttribute("data-values")
  );
  const yValues = JSON.parse(
    document.getElementById("compteur-par-jour-y").getAttribute("data-values")
  );
  const maxValeur = Math.max(...yValues);

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
        text: "Nombre de parties par jour ce mois-ci",
      },
      legend: { display: false },
      scales: {
        xAxes: [
          {
            scaleLabel: {
              display: true,
              labelString: "Jour",
            },
          },
        ],
        yAxes: [
          {
            scaleLabel: {
              display: true,
              labelString: "Nombre de parties",
            },
            ticks: {
              min: 0,
              max: maxValeur + 5,
            },
          },
        ],
      },
    },
  });
}