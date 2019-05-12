$(function () {
  /* ChartJS
   * -------
   * Data and config for chartjs
   */
  'use strict';

  var browserTrafficData = {
    datasets: [{
      data: [20, 20, 10, 30, 20],
      backgroundColor: [
        'rgba(255,99,132,1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(75, 192, 117, 1)',
        'rgba(255, 159, 64, 1)'
      ],
      borderColor: [
        'rgba(255,99,132,1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(75, 192, 117, 1)',
        'rgba(255, 159, 64, 1)'
      ],
    }],

    // These labels appear in the legend and in the tooltips when hovering different arcs
    labels: [
      'Firefox',
      'Safari',
      'Explorer',
      'Chrome',
      'Opera Mini'
    ]
  };


  var doughnutPieOptions = {
    responsive: true,
    animation: {
      animateScale: true,
      animateRotate: true
    }
  };

  if ($("#browserTrafficChart").length) {
    var doughnutChartCanvas = $("#browserTrafficChart").get(0).getContext("2d");
    var doughnutChart = new Chart(doughnutChartCanvas, {
      type: 'doughnut',
      data: browserTrafficData,
      // options: doughnutPieOptions
    });
  }
});