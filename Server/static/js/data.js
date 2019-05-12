$(function () {
  /* ChartJS
   * -------
   * Data and config for chartjs
   */
  'use strict';


  var lbl = ["bicchiere", "palettina", "caffe", "zucchero", "latte", "te", "cioccolato"];
  
  var val_1 = [80, 32, 45, 14, 52, 29, 96];
  var val_2 = [12, 42, 75, 23, 78, 32, 67];

  var options = {
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    },
    legend: {
      display: false
    },
    elements: {
      point: {
        radius: 0
      }
    }
  };


  var color_1 = [
    'rgba(255, 0, 0, 0.2)',
    'rgba(255, 165, 0, 0.2)',
    'rgba(255, 230, 0, 0.2)',
    'rgba(0, 180, 0, 0.2)',
    'rgba(90, 200, 255, 0.2)',
    'rgba(0, 0, 255, 0.2)',
    'rgba(238, 130, 238, 0.2)'
  ];

  var color_2 = [
    'rgba(255, 0, 0, 1)',
    'rgba(255, 165, 0, 1)',
    'rgba(255, 230, 0, 1)',
    'rgba(0, 180, 0, 1)',
    'rgba(90, 200, 255, 1)',
    'rgba(0, 0, 255, 1)',
    'rgba(238, 130, 238, 1)'
  ];

  var data1 = {
    labels: lbl,
    datasets: [{
      data: val_1,
      backgroundColor: color_1,
      borderColor: color_2,
      borderWidth: 1
    }]
  };


  if ($("#Machine-1").length) {
    var barChartCanvas = $("#Machine-1").get(0).getContext("2d");
    // This will get the first returned node in the jQuery collection.
    var barChart = new Chart(barChartCanvas, {
      type: 'bar',
      data: data1,
      options: options
    });
  }


  var data2 = {
    labels: lbl,
    datasets: [{
      data: val_2,
      backgroundColor: color_1,
      borderColor: color_2,
      borderWidth: 1
    }]
  };

  if ($("#Machine-2").length) {
    var barChartCanvas = $("#Machine-2").get(0).getContext("2d");
    // This will get the first returned node in the jQuery collection.
    var barChart = new Chart(barChartCanvas, {
      type: 'bar',
      data: data2,
      options: options
    });
  }

});