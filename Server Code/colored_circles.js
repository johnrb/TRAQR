/**
 * Creates a nice google map of sensor readings as colored circles.
 * Includes a legend and the ability to switch between datasets.
 *
 * To use with custom data, simply point data_location to a valid
 * json file. This should be structured similar to fake_data.json. 
 *
 * Author: Vince Kurtz
 *
 */

var data_location = 'datafiles/combined_data.json';

// global parameters for map
var map;
var goshen = {lat: 41.5644, lng: -85.8283};
var default_zoom = 16;  // bigger numbers are closer

// sensor scales
var co_max = 9;
var oz_max = 0.07;
var pm_max = 12;
var vo_max = 3;
var temp_max = 100;
var hum_max = 100;

// Default property/sensor reading
var default_prop = 'co';
var default_unit = 'ppm';
var default_max = co_max;

var min_date = 0;
var max_date = 100;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: default_zoom,
        center: goshen,
        mapTypeId: 'terrain',
        streetViewControl: false,
        scrollwheel: false
    });

    // Load geojson data
    map.data.loadGeoJson(data_location);

    // Display data from the default sensor
    map.data.setStyle(function(feature) {
        var magnitude = feature.getProperty(default_prop);
        return {
            icon: getCircle(magnitude,0,default_max)
        };
    });

    // Setup for Recenter Control Box
    var centerControlDiv = document.createElement('div');
    var centerControl = new CenterControl(centerControlDiv, map);
    centerControlDiv.index = 1;
    map.controls[google.maps.ControlPosition.LEFT_TOP].push(centerControlDiv);

    // Setup for Scroll Toggle Control Box
    var scrollControlDiv = document.createElement('div');
    var scrollControl = new ScrollControl(scrollControlDiv, map);
    scrollControlDiv.index = 1;
    map.controls[google.maps.ControlPosition.LEFT_TOP].push(scrollControlDiv);

    // Setup for Sensor Selection Control Box
    var sensorControlDiv = document.createElement('div');
    var sensorControl = new SensorControl(sensorControlDiv, map);
    sensorControlDiv.index = 2;
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(sensorControlDiv);

    // Set up the legend
    updateLegend(0,default_max,default_unit);
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(legend);

    // Set up slider control
    google.maps.event.addListenerOnce(map, 'idle', function() {
        // Do this once the data has been loaded
        var date_range = getDateRange();
        min_date = date_range[0];
        max_date = date_range[1];

        doubleSlider();  // initialize the slider
        var slider = document.getElementById('slider');
        map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(slider);
    });

    // Set up info windows
    var infowindow = new google.maps.InfoWindow();

    map.data.addListener('click', function(event) {
        var t = event.feature.getProperty("time");
        // now format the time nicely
        var time = t.substr(0,4)+"/"+t.substr(4,2)+"/"+t.substr(6,2)+" "+t.substr(8,2)+":"+t.substr(10,2)+":"+t.substr(12,2);
        var co = event.feature.getProperty("co");
        var oz = event.feature.getProperty("oz");
        var pm = event.feature.getProperty("pm");
        var vo = event.feature.getProperty("vo");
        var temp = event.feature.getProperty("temp");
        var hum = event.feature.getProperty("hum");
        var loc = event.feature.getGeometry().get();
        var contentString = "<div><b>Time:</b> "+time+"</div>" +
            "<div><b>Carbon Monoxide:</b> "+co+" ppm</div>" +
            "<div><b>Location:</b> "+loc+" </div>" +
            "<div><b>Ozone:</b> "+oz+" ppm</div>" +
            "<div><b>Particulate Matter:</b> "+pm+" ppm</div>" +
            "<div><b>Volatile Organics:</b> "+vo+" ppm</div>" +
            "<div><b>Temperature:</b> "+temp+" &deg;F</div>" +
            "<div><b>Humidity:</b> "+hum+" %</div>";
        infowindow.setContent(contentString);
        infowindow.setPosition(event.feature.getGeometry().get());
        infowindow.open(map)
    });

}

function doubleSlider() {
    // Create and update the double slider for date range calculation
    $( function() {
        my_min = Number(min_date.substr(2,6));   // use YYMMDD format so these values don't get too big
        my_max = Number(max_date.substr(2,6));
        $( "#slider-range" ).slider({
            range: true,
            min: my_min,
            max: my_max,
            values: [ my_min, my_max ],  // show all data by default
            slide: function( event, ui ) {
                setDisplayRange(ui.values[0], ui.values[1]);

                minimum = "20" + String(ui.values[0]).substr(0,2) + "/" + String(ui.values[0]).substr(2,2) + "/" + String(ui.values[0]).substr(4,2);
                maximum = "20" + String(ui.values[1]).substr(0,2) + "/" + String(ui.values[1]).substr(2,2) + "/" + String(ui.values[1]).substr(4,2);
                $( "#amount" ).val( " " + minimum + " - " + maximum );
            }
        });

        // Set the behavior on first load
        minimum = "20" + String(my_min).substr(0,2) + "/" + String(my_min).substr(2,2) + "/" + String(my_min).substr(4,2);
        maximum = "20" + String(my_max).substr(0,2) + "/" + String(my_max).substr(2,2) + "/" + String(my_max).substr(4,2);
        
        $( "#amount" ).val( minimum + " - " + maximum );
    });
}

function getDateRange() {
    // Return the most recent and oldest dates we could plot
    // This will be used to determine the ranges for the double Slider
    var max = 0;
    var min = 99999999999999;  // start with something way big
    map.data.forEach(function(i) {
        curr = i.getProperty("time");
        if (curr > max) {
            max = curr;
        } else if (curr < min) {
            min = curr;
        }
    });

    return [min, max];
}

function setDisplayRange(min_date, max_date) {
    // Reset the map to only display data from within the specified dates
    // min_date and max_date should be integers represending a date in YYMMDD format
    var new_data = {
            "type": "FeatureCollection",
            "features": []
        };
    var old_data;
    $.ajax({
      url: data_location,
      async: false,
      dataType: 'json',
      success: function (response) {
        old_data = response;
      }
    });
  
    for (i in old_data.features) {
        t = old_data.features[i].properties.time.substr(2,6);
        if (min_date <= t && t <= max_date) {
            new_data.features.push(old_data.features[i]); 
        }
    }

    map.data.forEach(function(i) { map.data.remove(i); });  // clear the map
    map.data.addGeoJson(new_data);      // add selected data back in
}

function reset_data_display(property, min, max) {
    // Display data corresponding to a new property
    // min and max define the expected data range for coloring purposes
    map.data.setStyle(function(feature) {
        var magnitude = feature.getProperty(property);
        return {
            icon: getCircle(magnitude, min, max)
        };
    });
}

function getCircle(magnitude, min, max) {
    var fill = getColor(magnitude,min,max);
    return {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: fill,
        fillOpacity: .5,
        scale: 10,
        strokeColor: 'white',
        strokeWeight: .5
    };
}

function getColor(val, min, max) {
    // choose a color that represents the value 'val' on  a scale
    // from min to max. Red is high, green is low.

    if (val > max) { val = max; }
    else if (val < min) { val = min; }

    var h = Math.floor((max - val) * 120 / max);
    var s = 1;
    var v = 1;

    return hsv2rgb(h,s,v);
}

function updateLegend(min,max,unit) {
    var legend = document.getElementById('legend');
    var div = document.createElement('div');
    var html = "<p style='text-align:center;'>" + max + " " + unit + "</p>";

    // Get representative colors
    var val;
    var color;
    var slots = 40;
    for (var i=slots; i>0; i--) {
        val = ((max-min)/(slots-1))*i+min;
        color = getColor(val,min,max);
        html += "<div style='text-align:center;width:40px;height:5px;background-color:"+color+";margin:1px;'></div>";
    }
    html += "<p style='text-align:center;'>" + min + " " + unit + "</p>";
    html += "<br />";
    html += "<div style='text-align:center;width:40px;height:5px;background-color:#555;margin:1px;'></div>";
    html += "<p style='text-align:center;'>no data</p>";
    div.innerHTML = html;
    legend.innerHTML = '<h3>Legend</h3>';  // clear old content, but keep the heading
    legend.appendChild(div);
}

function hsv2rgb(h, s, v) {
    // adapted from http://schinckel.net/2012/01/10/hsv-to-rgb-in-javascript/
    var rgb, i, data = [];
    if (s === 0) {
        rgb = [v,v,v];
    } else {
        h = h / 60;
        i = Math.floor(h);
        data = [v*(1-s), v*(1-s*(h-i)), v*(1-s*(1-(h-i)))];
        switch(i) {
            case 0:
                rgb = [v, data[2], data[0]];
                break;
            case 1:
                rgb = [data[1], v, data[0]];
                break;
            case 2:
                rgb = [data[0], v, data[2]];
                break;
            case 3:
                rgb = [data[0], data[1], v];
                break;
            case 4:
                rgb = [data[2], data[0], v];
                break;
            default:
                rgb = [v, data[0], data[1]];
                break;
        }
    }
    return '#' + rgb.map(function(x){
        return ("0" + Math.round(x*255).toString(16)).slice(-2);
    }).join('');
};

function CenterControl(controlDiv, map) {
    // create control box to recenter the map 
    // @constructor

    // Set CSS for the control border.
    var controlUI = document.createElement('div');
    controlUI.style.backgroundColor = '#fff';
    controlUI.style.border = '2px solid #fff';
    controlUI.style.borderRadius = '3px';
    controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
    controlUI.style.cursor = 'pointer';
    controlUI.style.marginBottom = '22px';
    controlUI.style.marginLeft = '10px';
    controlUI.style.textAlign = 'center';
    controlUI.title = 'Click to recenter the map';
    controlDiv.appendChild(controlUI);

    // Set CSS for the control interior.
    var controlText = document.createElement('div');
    controlText.style.color = 'rgb(25,25,25)';
    controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
    controlText.style.fontSize = '12px';
    controlText.style.lineHeight = '20px';
    controlText.style.paddingLeft = '5px';
    controlText.style.paddingRight = '5px';
    controlText.innerHTML = 'Re-center Map';
    controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to look at GC
    controlUI.addEventListener('click', function() {
        map.setCenter(goshen);
        map.setZoom(default_zoom);
    });

}

function ScrollControl(controlDiv, map) {
    // create control box to toggle scroll-to-zoom
    // @constructor

    // Set CSS for the control border.
    var controlUI = document.createElement('div');
    controlUI.style.backgroundColor = '#fff';
    controlUI.style.border = '2px solid #fff';
    controlUI.style.borderRadius = '3px';
    controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
    controlUI.style.cursor = 'pointer';
    controlUI.style.marginBottom = '22px';
    controlUI.style.marginLeft = '10px';
    controlUI.style.textAlign = 'center';
    controlUI.title = 'Toggle scroll-to-zoom';
    controlDiv.appendChild(controlUI);

    // Set CSS for the control interior.
    var controlText = document.createElement('div');
    controlText.style.color = 'rgb(25,25,25)';
    controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
    controlText.style.fontSize = '12px';
    controlText.style.lineHeight = '20px';
    controlText.style.paddingLeft = '5px';
    controlText.style.paddingRight = '5px';
    controlText.style.fontWeight = 'lighter';
    controlText.innerHTML = 'Scroll-to-Zoom Disabled';
    controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to look at GC
    controlUI.addEventListener('click', function() {
        var on = map.get('scrollwheel');
        if (on) {
            map.set('scrollwheel', false);
            controlText.style.fontWeight = 'lighter';
            controlText.innerHTML = 'Scroll-to-Zoom Disabled';
        } else {
            map.set('scrollwheel', true);
            controlText.style.fontWeight = 'bold';
            controlText.innerHTML = 'Scroll-to-Zoom Enabled';
        }
    });

}
function SensorControl(controlDiv, map) {
    // Create control box to select which sensor data to display
    // @constructor

    // Set CSS for the control border.
    var controlBox = document.createElement('div');
    controlBox.style.backgroundColor = '#fff';
    //controlBox.style.border = '2px solid #fff';
    controlBox.style.borderRadius = '3px';
    controlBox.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
    controlBox.style.cursor = 'pointer';
    controlBox.style.marginBottom = '22px';
    controlBox.style.marginTop = '10px';
    controlBox.style.textAlign = 'center';
    controlBox.style.display = 'table';
    controlBox.title = 'Select which data to display';
    controlDiv.appendChild(controlBox);

    // Set CSS for the control interior.
    var sensor1Text = document.createElement('div');
    sensor1Text.style.color = 'rgb(25,25,25)';
    sensor1Text.style.fontFamily = 'Roboto,Arial,sans-serif';
    sensor1Text.style.fontSize = '14px';
    sensor1Text.style.lineHeight = '30px';
    sensor1Text.style.paddingLeft = '5px';
    sensor1Text.style.paddingRight = '5px';
    sensor1Text.style.display = 'table-cell';
    sensor1Text.style.fontWeight = 'bold';
    sensor1Text.style.borderRight = '1px solid #ddd';
    sensor1Text.innerHTML = 'Carbon Monoxide';
    controlBox.appendChild(sensor1Text);

    var sensor2Text = document.createElement('div');
    sensor2Text.style.color = 'rgb(25,25,25)';
    sensor2Text.style.fontFamily = 'Roboto,Arial,sans-serif';
    sensor2Text.style.fontSize = '14px';
    sensor2Text.style.lineHeight = '30px';
    sensor2Text.style.paddingLeft = '5px';
    sensor2Text.style.paddingRight = '5px';
    sensor2Text.style.display = 'table-cell';
    sensor2Text.style.fontWeight = 'normal';
    sensor2Text.style.borderRight = '1px solid #ddd';
    sensor2Text.innerHTML = 'Ozone';
    controlBox.appendChild(sensor2Text);

    var sensor3Text = document.createElement('div');
    sensor3Text.style.color = 'rgb(25,25,25)';
    sensor3Text.style.fontFamily = 'Roboto,Arial,sans-serif';
    sensor3Text.style.fontSize = '14px';
    sensor3Text.style.lineHeight = '30px';
    sensor3Text.style.paddingLeft = '5px';
    sensor3Text.style.paddingRight = '5px';
    sensor3Text.style.display = 'table-cell';
    sensor3Text.style.fontWeight = 'normal';
    sensor3Text.style.borderRight = '1px solid #ddd';
    sensor3Text.innerHTML = 'Particulate Matter';
    controlBox.appendChild(sensor3Text);

    var sensor4Text = document.createElement('div');
    sensor4Text.style.color = 'rgb(25,25,25)';
    sensor4Text.style.fontFamily = 'Roboto,Arial,sans-serif';
    sensor4Text.style.fontSize = '14px';
    sensor4Text.style.lineHeight = '30px';
    sensor4Text.style.paddingLeft = '5px';
    sensor4Text.style.paddingRight = '5px';
    sensor4Text.style.display = 'table-cell';
    sensor4Text.style.fontWeight = 'normal';
    sensor4Text.style.borderRight = '1px solid #ddd';
    sensor4Text.innerHTML = 'Volatile Organics';
    controlBox.appendChild(sensor4Text);

    var sensor5Text = document.createElement('div');
    sensor5Text.style.color = 'rgb(25,25,25)';
    sensor5Text.style.fontFamily = 'Roboto,Arial,sans-serif';
    sensor5Text.style.fontSize = '14px';
    sensor5Text.style.lineHeight = '30px';
    sensor5Text.style.paddingLeft = '5px';
    sensor5Text.style.paddingRight = '5px';
    sensor5Text.style.display = 'table-cell';
    sensor5Text.style.fontWeight = 'normal';
    sensor5Text.style.borderRight = '1px solid #ddd';
    sensor5Text.innerHTML = 'Temperature';
    controlBox.appendChild(sensor5Text);

    var sensor6Text = document.createElement('div');
    sensor6Text.style.color = 'rgb(25,25,25)';
    sensor6Text.style.fontFamily = 'Roboto,Arial,sans-serif';
    sensor6Text.style.fontSize = '14px';
    sensor6Text.style.lineHeight = '30px';
    sensor6Text.style.paddingLeft = '5px';
    sensor6Text.style.paddingRight = '5px';
    sensor6Text.style.display = 'table-cell';
    sensor6Text.style.fontWeight = 'normal';
    sensor6Text.innerHTML = 'Humidity';
    controlBox.appendChild(sensor6Text);

    // Setup the click event listeners
    sensor1Text.addEventListener('click', function() {
        sensor1Text.style.fontWeight = 'bold';
        sensor2Text.style.fontWeight = 'normal';
        sensor3Text.style.fontWeight = 'normal';
        sensor4Text.style.fontWeight = 'normal';
        sensor5Text.style.fontWeight = 'normal';
        sensor6Text.style.fontWeight = 'normal';

        reset_data_display('co',0,co_max);
        updateLegend(0,co_max,'ppm');
    });
    sensor2Text.addEventListener('click', function() {
        sensor1Text.style.fontWeight = 'normal';
        sensor2Text.style.fontWeight = 'bold';
        sensor3Text.style.fontWeight = 'normal';
        sensor4Text.style.fontWeight = 'normal';
        sensor5Text.style.fontWeight = 'normal';
        sensor6Text.style.fontWeight = 'normal';

        reset_data_display('oz',0,oz_max);
        updateLegend(0,oz_max,'ppm');
    });
    sensor3Text.addEventListener('click', function() {
        sensor1Text.style.fontWeight = 'normal';
        sensor2Text.style.fontWeight = 'normal';
        sensor3Text.style.fontWeight = 'bold';
        sensor4Text.style.fontWeight = 'normal';
        sensor5Text.style.fontWeight = 'normal';
        sensor6Text.style.fontWeight = 'normal';

        reset_data_display('pm',0,pm_max);
        updateLegend(0,pm_max,'ppm');
    });
    sensor4Text.addEventListener('click', function() {
        sensor1Text.style.fontWeight = 'normal';
        sensor2Text.style.fontWeight = 'normal';
        sensor3Text.style.fontWeight = 'normal';
        sensor4Text.style.fontWeight = 'bold';
        sensor5Text.style.fontWeight = 'normal';
        sensor6Text.style.fontWeight = 'normal';

        reset_data_display('vo',0,vo_max);
        updateLegend(0,vo_max,'ppm');
    });
    sensor5Text.addEventListener('click', function() {
        sensor1Text.style.fontWeight = 'normal';
        sensor2Text.style.fontWeight = 'normal';
        sensor3Text.style.fontWeight = 'normal';
        sensor4Text.style.fontWeight = 'normal';
        sensor5Text.style.fontWeight = 'bold';
        sensor6Text.style.fontWeight = 'normal';

        reset_data_display('temp',0,temp_max);
        updateLegend(0,temp_max,'&deg;F');
    });
    sensor6Text.addEventListener('click', function() {
        sensor1Text.style.fontWeight = 'normal';
        sensor2Text.style.fontWeight = 'normal';
        sensor3Text.style.fontWeight = 'normal';
        sensor4Text.style.fontWeight = 'normal';
        sensor5Text.style.fontWeight = 'normal';
        sensor6Text.style.fontWeight = 'bold';

        reset_data_display('hum',0,hum_max);
        updateLegend(0,hum_max,'&#37;'); // that's a percent sign
    });
}
