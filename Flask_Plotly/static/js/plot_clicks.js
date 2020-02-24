let interval = 500;
let doubleClickTime = 0;

var myPlot = document.getElementsByClassName('js-plotly-plot')[0]
myPlot.on('plotly_click', ClickHandler);
myPlot.on('plotly_doubleclick', doubleClickHandler);

function ClickHandler(data) {
  let t0 = Date.now();

  // second click
  if ((t0 - doubleClickTime) < interval) {
	  document.getElementsByName("b_wave_length")[0].value = data.points[0].x
  }else{
    setTimeout(function() {
	    // first click
      if ((t0 - doubleClickTime) > interval) {
	      document.getElementsByName("wave_length")[0].value = data.points[0].x
      }
    }, interval);
  }
}

function doubleClickHandler() {
	doubleClickTime = Date.now();
}
