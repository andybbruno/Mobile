$(function () {
  /* ChartJS
   * -------
   * Data and config for chartjs
   */
  'use strict';

  
  function loadFile(filePath) {
    var result = null;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", filePath, false);
    xmlhttp.send();
    if (xmlhttp.status == 200) {
      result = xmlhttp.responseText;
    }
    return result;
  }


  var val_1 = loadFile("/static/data/val_1.txt").split(',');
  var val_2 = loadFile("/static/data/val_2.txt").split(',');
  var lbl = loadFile("/static/data/lbl.txt").split(',');

  
  var options = {
    responsive: true,
    legend: {
      position: 'right',
    },
    title: {
      display: true,
      text: ' '
    },
    scale: {
      ticks: {
        min: 0,
        max: 100,
        beginAtZero: true
      },
      reverse: false
    },
    animation: {
      animateRotate: false,
      animateScale: true
    }
  };


  var color_1 = [
    'rgba(255, 0, 0, 0.7)',
    'rgba(255, 165, 0, 0.7)',
    'rgba(255, 230, 0, 0.7)',
    'rgba(0, 180, 0, 0.7)',
    'rgba(90, 200, 255, 0.7)',
    'rgba(0, 0, 255, 0.7)',
    'rgba(238, 130, 238, 0.7)'
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
      borderColor: '#fff',
      borderWidth: 2
    }]
  };


  if ($("#Machine-1").length) {
    var chartID = $("#Machine-1").get(0).getContext("2d");
    // This will get the first returned node in the jQuery collection.
    var ctx = new Chart(chartID, {
      type: 'polarArea',
      data: data1,
      options: options
    });
  }


  var data2 = {
    labels: lbl,
    datasets: [{
      data: val_2,
      backgroundColor: color_1,
      borderColor: '#fff',
      borderWidth: 2
    }]
  };

  if ($("#Machine-2").length) {
    var chartID = $("#Machine-2").get(0).getContext("2d");
    // This will get the first returned node in the jQuery collection.
    var ctx = new Chart(chartID, {
      type: 'polarArea',
      data: data2,
      options: options
    });
  }

});