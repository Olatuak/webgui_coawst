"use strict";

/*
 Generic  Canvas Layer for leaflet 0.7 and 1.0-rc,
 copyright Stanislav Sumbera,  2016 , sumbera.com , license MIT
 originally created and motivated by L.CanvasOverlay  available here: https://gist.github.com/Sumbera/11114288

 */

var areCoordinatesDirty = false;    // Coordinates are dirty after a zoom or a pan and before the new transformations are computed
var context = null;                 // WARNING: This assumes that there is only one heatmap layer, which is an unreasonable assumption


// -- L.DomUtil.setTransform from leaflet 1.0.0 to work on 0.0.7
//------------------------------------------------------------------------------
if (!L.DomUtil.setTransform) {
  L.DomUtil.setTransform = function (el, offset, scale) {
    var pos = offset || new L.Point(0, 0);
    el.style[L.DomUtil.TRANSFORM] = (L.Browser.ie3d ? "translate(" + pos.x + "px," + pos.y + "px)" : "translate3d(" + pos.x + "px," + pos.y + "px,0)") + (scale ? " scale(" + scale + ")" : "");
  };
} // -- support for both  0.0.7 and 1.0.0 rc2 leaflet


L.CanvasLayer = (L.Layer ? L.Layer : L.Class).extend({
  // -- initialized is called on prototype
  initialize: function initialize(options) {
    this._map = null;
    this._canvas = null;
    this._frame = null;
    this._delegate = null;
    L.setOptions(this, options);
  },
  delegate: function delegate(del) {
    this._delegate = del;
    return this;
  },
  needRedraw: function needRedraw() {
    if (!this._frame) {
      this._frame = L.Util.requestAnimFrame(this.drawLayer, this);
    }

    return this;
  },
  //-------------------------------------------------------------
  _onLayerDidResize: function _onLayerDidResize(resizeEvent) {
    this._canvas.width = resizeEvent.newSize.x;
    this._canvas.height = resizeEvent.newSize.y;
  },
  //-------------------------------------------------------------
  _onLayerDidMove: function _onLayerDidMove() {

    var topLeft = this._map.containerPointToLayerPoint([0, 0]);

    L.DomUtil.setPosition(this._canvas, topLeft);
console.log('dasjkjdalkdjsaldjsaldkjsalkdjsaldjsakl111111')
    this.drawLayer();
  },
  //-------------------------------------------------------------
  getEvents: function getEvents() {
    var events = {
      resize: this._onLayerDidResize,
      moveend: this._onLayerDidMove
    };

    if (this._map.options.zoomAnimation && L.Browser.any3d) {
      events.zoomanim = this._animateZoom;
    }

    return events;
  },
  //-------------------------------------------------------------
  onAdd: function onAdd(map) {
    this._map = map;
    this._canvas = L.DomUtil.create("canvas", "leaflet-layer");
    this.tiles = {};

    var size = this._map.getSize();

    this._canvas.width = size.x;
    this._canvas.height = size.y;
    var animated = this._map.options.zoomAnimation && L.Browser.any3d;
    L.DomUtil.addClass(this._canvas, "leaflet-zoom-" + (animated ? "animated" : "hide"));
    this.options.pane.appendChild(this._canvas);
    map.on(this.getEvents(), this);
    var del = this._delegate || this;
    del.onLayerDidMount && del.onLayerDidMount(); // -- callback

    this.needRedraw();
    var self = this;
    setTimeout(function () {
      self._onLayerDidMove();
    }, 0);
  },
  //-------------------------------------------------------------
  onRemove: function onRemove(map) {
    var del = this._delegate || this;
    del.onLayerWillUnmount && del.onLayerWillUnmount(); // -- callback

    this.options.pane.removeChild(this._canvas);
    map.off(this.getEvents(), this);
    this._canvas = null;
  },
  //------------------------------------------------------------
  addTo: function addTo(map) {
    map.addLayer(this);
    return this;
  },
  //------------------------------------------------------------------------------
  drawLayer: function drawLayer() {
    // -- todo make the viewInfo properties  flat objects.
    var size = this._map.getSize();

    var bounds = this._map.getBounds();

    var zoom = this._map.getZoom();

    var center = this._map.options.crs.project(this._map.getCenter());

    var corner = this._map.options.crs.project(this._map.containerPointToLatLng(this._map.getSize()));

    var del = this._delegate || this;
    del.onDrawLayer && del.onDrawLayer({
      layer: this,
      canvas: this._canvas,
      bounds: bounds,
      size: size,
      zoom: zoom,
      center: center,
      corner: corner
    });
    this._frame = null;
  },
  // -- L.DomUtil.setTransform from leaflet 1.0.0 to work on 0.0.7
  //------------------------------------------------------------------------------
  _setTransform: function _setTransform(el, offset, scale) {
    var pos = offset || new L.Point(0, 0);
    el.style[L.DomUtil.TRANSFORM] = (L.Browser.ie3d ? "translate(" + pos.x + "px," + pos.y + "px)" : "translate3d(" + pos.x + "px," + pos.y + "px,0)") + (scale ? " scale(" + scale + ")" : "");
  },
  //------------------------------------------------------------------------------
  _animateZoom: function _animateZoom(e) {
    var scale = this._map.getZoomScale(e.zoom); // -- different calc of offset in leaflet 1.0.0 and 0.0.7 thanks for 1.0.0-rc2 calc @jduggan1


    var offset = L.Layer ? this._map._latLngToNewLayerPoint(this._map.getBounds().getNorthWest(), e.zoom, e.center) : this._map._getCenterOffset(e.center)._multiplyBy(-scale).subtract(this._map._getMapPanePos());
    L.DomUtil.setTransform(this._canvas, offset, scale);
  }
});

L.canvasLayer = function (pane) {
  return new L.CanvasLayer(pane);
};

L.Control.Heatmap = L.Control.extend({
  options: {
    position: "bottomleft",
    emptyString: "Unavailable",
    // Could be any combination of 'bearing' (angle toward which the flow goes) or 'meteo' (angle from which the flow comes)
    // and 'CW' (angle value increases clock-wise) or 'CCW' (angle value increases counter clock-wise)
    angleConvention: "bearingCCW",
    showCardinal: false,
    // Could be 'm/s' for meter per second, 'k/h' for kilometer per hour, 'mph' for miles per hour or 'kt' for knots
    speedUnit: "m/s",
    directionString: "Direction",
    speedString: "Speed",
    onAdd: null,
    onRemove: null
  },
  onAdd: function onAdd(map) {
    this._container = L.DomUtil.create("div", "leaflet-control-heatmap");
    L.DomEvent.disableClickPropagation(this._container);
    map.on("mousemove", this._onMouseMove, this);
    this._container.innerHTML = this.options.emptyString;
    if (this.options.leafletHeatmap.options.onAdd) this.options.leafletHeatmap.options.onAdd();
    return this._container;
  },
  onRemove: function onRemove(map) {
    map.off("mousemove", this._onMouseMove, this);
    if (this.options.leafletHeatmap.options.onRemove) this.options.leafletHeatmap.options.onRemove();
  },

  _onMouseMove: function _onMouseMove(e) {
    var self = this;

    var pos = this.options.leafletHeatmap._map.containerPointToLatLng(L.point(e.containerPoint.x, e.containerPoint.y));

    var gridValue = this.options.leafletHeatmap._heat.interpolatePoint(pos.lng, pos.lat);

    var htmlOut = "";

    if (gridValue && !isNaN(gridValue[0]) && !isNaN(gridValue[1]) && gridValue[2]) {
      var deg = self.vectorToDegrees(gridValue[0], gridValue[1], this.options.angleConvention);
      var cardinal = this.options.showCardinal ? " (".concat(self.degreesToCardinalDirection(deg), ") ") : '';
      htmlOut = "<strong> ".concat(this.options.HeatmapType, " ").concat(this.options.directionString, ": </strong> ").concat(deg.toFixed(2), "\xB0").concat(cardinal, ", <strong> ").concat(this.options.HeatmapType, " ").concat(this.options.speedString, ": </strong> ").concat(self.vectorToSpeed(gridValue[0], gridValue[1], this.options.speedUnit).toFixed(2), " ").concat(this.options.speedUnit);
    } else {
      htmlOut = this.options.emptyString;
    }

    self._container.innerHTML = htmlOut;
  }
});

L.Map.mergeOptions({
  positionControl: false
});

L.Map.addInitHook(function () {
  if (this.options.positionControl) {
    this.positionControl = new L.Control.MousePosition();
    this.addControl(this.positionControl);
  }
});

L.control.Heatmap = function (options) {
  return new L.Control.Heatmap(options);
};

L.HeatmapLayer = (L.Layer ? L.Layer : L.Class).extend({
  options: {
    displayValues: true,
    displayOptions: {
      heatmapType: "heat",
      position: "bottomleft",
      emptyString: "No data"
    },
    maxValue: 10,
    // used to align color scale
    colorScale: null,
    data: null
  },
  _map: null,
  _canvasLayer: null,
  _heat: null,
  _context: null,
  _timer: 0,
  _mouseControl: null,
  initialize: function initialize(options) {
    L.setOptions(this, options);
  },
  onAdd: function onAdd(map) {
    // determine where to add the layer
    this._paneName = this.options.paneName || "overlayPane"; // fall back to overlayPane for leaflet < 1

    var pane = map._panes.overlayPane;

    if (map.getPane) {
      // attempt to get pane first to preserve parent (createPane voids this)
      pane = map.getPane(this._paneName);

      if (!pane) {
        pane = map.createPane(this._paneName);
      }
    } // create canvas, add to map pane


    this._canvasLayer = L.canvasLayer({
      pane: pane
    }).delegate(this);

    this._canvasLayer.addTo(map);

    this._map = map;
  },
  onRemove: function onRemove(map) {
    this._destroyHeat();
  },
  setData: function setData(data) {
    this.options.data = data;

    if (this._heat) {
      this._heat.setData(data);

      this._clearAndRestart();
    }

    this.fire("load");
  },
  setOpacity: function setOpacity(opacity) {
    this._canvasLayer.setOpacity(opacity);
  },
  setOptions: function setOptions(options) {
    this.options = Object.assign(this.options, options);

    if (options.hasOwnProperty("displayOptions")) {
      this.options.displayOptions = Object.assign(this.options.displayOptions, options.displayOptions);

      this._initMouseHandler(true);
    }

    if (options.hasOwnProperty("data")) this.options.data = options.data;

    if (this._heat) {
      this._heat.setOptions(options);

      if (options.hasOwnProperty("data")) this._heat.setData(options.data);

      this._clearAndRestart();
    }

    this.fire("load");
  },

  /*------------------------------------ PRIVATE ------------------------------------------*/
  onDrawLayer: function onDrawLayer(overlay, params) {
    var self = this;

    if (!this._heat) {
      this._initHeat(this);

      return;
    }

    if (!this.options.data) {
      return;
    }

    if (this._timer) clearTimeout(self._timer);
    this._timer = setTimeout(function () {
      self._startHeat();
    }, 10); // showing data is delayed. JMG: why? (used to be 750)
  },
  _startHeat: function _startHeat() {
    var bounds = this._map.getBounds();

    var size = this._map.getSize(); // bounds, width, height, extent


    this._heat.start([[0, 0], [size.x, size.y]], size.x, size.y, [[bounds._southWest.lng, bounds._southWest.lat], [bounds._northEast.lng, bounds._northEast.lat]]);
  },
  _initHeat: function _initHeat(self) {
    // heat object, copy options
    var options = Object.assign({
      canvas: self._canvasLayer._canvas,
      map: this._map
    }, self.options);
    this._heat = new Heat(options); // prepare context global var, start drawing

    this._context = this._canvasLayer._canvas.getContext("2d");
    context = this._canvasLayer._canvas.getContext("2d");

    this._canvasLayer._canvas.classList.add("heatmap-overlay");
    this.onDrawLayer();


    this._map.on("dragstart", self._heat.stop);

    this._map.on("dragend", self._clearAndRestart);

    this._map.on("zoomstart", self._heat.stop);

    this._map.on("zoomend", self._clearAndRestart);

    this._map.on("resize", self._clearHeat);

    this._initMouseHandler(false);
  },
  _initMouseHandler: function _initMouseHandler(voidPrevious) {
    if (voidPrevious) {
      this._map.removeControl(this._mouseControl);

      this._mouseControl = false;
    }

    if (!this._mouseControl && this.options.displayValues) {
      var options = this.options.displayOptions || {};
      options["leafletHeatmap"] = this;
      this._mouseControl = L.control.heatmap(options).addTo(this._map);
    }
  },
  _clearAndRestart: function _clearAndRestart(event) {
    areCoordinatesDirty = true;

    if (context)
    {
      context.globalAlpha = 1;
      context.clearRect(0, 0, 30000, 30000);
    }
    if (this._heat) this._startHeat();
  },
  _clearHeat: function _clearHeat() {
    if (this._heat) this._heat.stop();
    if (context)
    {
      context.globalAlpha = 1;
      context.clearRect(0, 0, 30000, 30000);
    }
  },
  _destroyHeat: function _destroyHeat() {
    if (this._timer) clearTimeout(this._timer);
    if (this._heat) this._heat.stop();
    if (context)
    {
      context.globalAlpha = 1;
      context.clearRect(0, 0, 30000, 30000);
    }
    if (this._mouseControl) this._map.removeControl(this._mouseControl);
    this._mouseControl = null;
    this._heat = null;
    this._map.removeLayer(this._canvasLayer);
  }
});


L.heatmapLayer = function (options) {
  return new L.HeatmapLayer(options);
};






var Heat = function Heat(params) {
  var MIN_VALUE = params.minValue || 0;
  var MAX_VALUE = params.maxValue || 10;


  var builder;
  var grid;
  var gridData = params.data;
  var date;
  var λ0, φ0, Δλ, Δφ, ni, nj, λg, φg, useΔ;

  var setData = function setData(data) {
    gridData = data;
  };

  var setOptions = function setOptions(options) {
    if (options.hasOwnProperty("minValue")) MIN_VALUE = options.minValue;
    if (options.hasOwnProperty("maxValue")) MAX_VALUE = options.maxValue;
  };


  var bilinearInterpolateVector = function bilinearInterpolateVector(x, y, g00, g10, g01, g11) {
    // x, y are between 0 and 1.
    var rx = 1 - x;
    var ry = 1 - y;

    var a = rx * ry,
        b = x  * ry,
        c = rx * y,
        d = x  * y;

    var v = g00[1]*a + g10[1]*b + g01[1]*c + g11[1]*d;

    return v;
  };

  var createHeatBuilder = function createHeatBuilder(v) {
    var vData = v.data;
    return {
      header: v.header,
      //recipe: recipeFor("heat-" + uComp.header.surface1Value),
      data: function data(i) {
        return vData[i];
      },
      interpolate: bilinearInterpolateVector
    };
  };

  var createBuilder = function createBuilder(data) {
    var v = null;
    data.forEach(function (record) {
      switch (record.header.parameterCategory + "," + record.header.parameterNumber) {
      AAAAAAAAAAAAAA
        case "1,2":
        case "2,2":
          uComp = record;
          break;

        case "1,3":
        case "2,3":
          vComp = record;
          break;

        default:
          scalar = record;
      }
    });
    return createHeatBuilder(uComp, vComp);
  };


  var buildGrid = function buildGrid(data, callback) {
    var supported = true;
    if (data.length > 1) supported = false;
    if (!supported) console.log("Heat Error: data must have only one component");
    builder = createBuilder(data);
    var header = builder.header;
    if (header.hasOwnProperty("gridDefinitionTemplate") && header.gridDefinitionTemplate != 0) supported = false;

    if (!supported) {
      console.log("Heat Error: Only data with Latitude_Longitude coordinates is supported");
    }

    supported = true; // reset for futher checks

    useΔ = (typeof header.dx !== 'undefined')  // True if the grid is defined by deltas.
    if (useΔ)
    {
        λ0 = header.lo1;
        φ0 = header.la1; // the grid's origin (e.g., 0.0E, 90.0N)

        Δλ = header.dx;
        Δφ = header.dy; // distance between grid points (e.g., 2.5 deg lon, 2.5 deg lat)

        ni = header.nx;
        nj = header.ny; // number of grid points W-E and N-S (e.g., 144 x 73)
    }
    else
    {
        λg = header.lon
        φg = header.lat

        Δλ = 0
        Δφ = 0

        ni = λg.length
        nj = φg.length
    }

    if (header.hasOwnProperty("scanMode")) {
      var scanModeMask = header.scanMode.toString(2);
      scanModeMask = ('0' + scanModeMask).slice(-8);
      var scanModeMaskArray = scanModeMask.split('').map(Number).map(Boolean);
      if (scanModeMaskArray[0]) Δλ = -Δλ;
      if (scanModeMaskArray[1]) Δφ = -Δφ;
      if (scanModeMaskArray[2]) supported = false;
      if (scanModeMaskArray[3]) supported = false;
      if (scanModeMaskArray[4]) supported = false;
      if (scanModeMaskArray[5]) supported = false;
      if (scanModeMaskArray[6]) supported = false;
      if (scanModeMaskArray[7]) supported = false;
      if (!supported) console.log("Heat Error: Data with scanMode: " + header.scanMode + " is not supported.");
    }

    date = new Date(header.refTime);
    date.setHours(date.getHours() + header.forecastTime); // Scan modes 0, 64 allowed.
    // http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table3-4.shtml

    grid = [];
    var p = 0;
    var isContinuous = Math.floor(ni * Δλ) >= 360;

    for (var j = 0; j < nj; j++) {
      var row = [];

      for (var i = 0; i < ni; i++, p++) {
        row[i] = builder.data(p);
      }

      if (isContinuous) {
        // For wrapped grids, duplicate first column as last column to simplify interpolation logic
        row.push(row[0]);
      }

      grid[j] = row;
    }

    callback({
      date: date,
      interpolate: interpolate
    });
  };
  /**
   * Get interpolated grid value from Lon/Lat position
   * @param λ {Float} Longitude
   * @param φ {Float} Latitude
   * @returns {Object}
   */

  const binarySearch = (arr, val) => {
    let l = 0,
    r = arr.length;
    while (r - l > 1) {
      const m = Math.floor((l + r) / 2);
      const guess = arr[m];
      if (guess > val) r = m;
      else l = m;
    }
    return l;
  };

  var interpolate = function interpolate(λ, φ) {
    if (!grid) return null;

    var fi, fj, ci, cj

    if (useΔ)
    {
        var i = floorMod(λ - λ0, 360) / Δλ; // calculate longitude index in wrapped range [0, 360)

        var j = (φ0 - φ) / Δφ; // calculate latitude index in direction +90 to -90

        var fi = Math.floor(i),
            ci = fi + 1;
        var fj = Math.floor(j),
            cj = fj + 1;
    }
    else
    {
        fi = binarySearch(λg, λ)
        fj = binarySearch(φg, φ)
        ci = fi + 1;
        cj = fj + 1;
        var i = (λ - λg[fi])/(λg[ci] - λg[fi]) + fi   // i, j are not integers, no matter how innocent they look.
        var j = (φ - φg[fj])/(φg[cj] - φg[fj]) + fj
    }

    var row;

    if (row = grid[fj]) {
      var g00 = row[fi];
      var g10 = row[ci];

      // Notice 'row = grid[cj]' is an assignment.
      if (isValue(g00) && isValue(g10) && (row = grid[cj])) {
        var g01 = row[fi];
        var g11 = row[ci];

        if (isValue(g01) && isValue(g11)) {
          // All four points found, so interpolate the value.
          return builder.interpolate(i - fi, j - fj, g00, g10, g01, g11);
        }
      }
    }

    return null;
  };


  var isValue = function isValue(x) {
  /// @returns {Boolean} true if the specified value is not null and not undefined.
    return x !== null && x !== undefined;
  };


  var floorMod = function floorMod(a, n) {
  /// @returns {Number} returns remainder of floored division, i.e., floor(a / n). Useful for consistent modulo
   *          of negative numbers. See http://en.wikipedia.org/wiki/Modulo_operation.
    return a - n * Math.floor(a / n);
  };


  var clamp = function clamp(x, range) {
  /// @returns {Number} the value x clamped to the range [low, high].
    return Math.max(range[0], Math.min(x, range[1]));
  };


  var isMobile = function isMobile() {
  /// @returns {Boolean} true if agent is probably a mobile device. Don't really care if this is accurate.
    return /android|blackberry|iemobile|ipad|iphone|ipod|opera mini|webos/i.test(navigator.userAgent);
  };


  var createField = function createField(columns, bounds, callback) {


    function field(x, y) {
    // @returns {Array} heat magnitude at the point (x, y), NaN if it doesn't exist
      var column = columns[Math.round(x)];
      return column && column[Math.round(y)] || null;
    }

    // Frees the massive "columns" array for GC. Without this, the array is leaked (in Chrome) each time a new
    // field is interpolated because the field closure's context is leaked, for reasons that defy explanation.
    field.release = function () {
      columns = [];
    };

    field.randomize = function (o) {
      // UNDONE: this method is terrible
      var x, y;
      var safetyNet = 0;  // It doesn't try more than 30 times to find an empty place (VERY unlikely to happen in normal conditions).

      // Avoids to repeat the same point twice
      do {
        x = Math.round(Math.floor(Math.random() * bounds.width ) + bounds.x);
        y = Math.round(Math.floor(Math.random() * bounds.height) + bounds.y);

        // if field(x, y)[2] is null it means that it is land, I'm not sure what NaN means
      } while ((field(x, y)[2] === null || isNaN(field(x, y)[2])) && safetyNet++ < 30);

      o.x = x;
      o.y = y;

      return o;
    };



    callback(bounds, field);
  };

  var buildBounds = function buildBounds(bounds, width, height) {
    var upperLeft = bounds[0];
    var lowerRight = bounds[1];
    var x = Math.round(upperLeft[0]); //Math.max(Math.floor(upperLeft[0], 0), 0);

    var y = Math.max(Math.floor(upperLeft[1], 0), 0);
    var xMax = Math.min(Math.ceil(lowerRight[0], width), width - 1);
    var yMax = Math.min(Math.ceil(lowerRight[1], height), height - 1);
    return {
      x: x,
      y: y,
      xMax: width,
      yMax: yMax,
      width: width,
      height: height
    };
  };

  var deg2rad = function deg2rad(deg) {
    return deg / 180 * Math.PI;
  };

  var invert = function invert(x, y, heat) {
    var latlon = params.map.containerPointToLatLng(L.point(x, y));
    return [latlon.lng, latlon.lat];
  };

  var project = function project(lat, lon, heat) {
    var xy = params.map.latLngToContainerPoint(L.latLng(lat, lon));
    return [xy.x, xy.y];
  };

  var interpolateField = function interpolateField(grid, bounds, extent, callback) {
    var projection = {}; // map.crs used instead

    var mapArea = (extent.south - extent.north) * (extent.west - extent.east);
    var columns = [];
    var x = bounds.x;

    function interpolateColumn(x) {
      var column = [];

      for (var y = bounds.y; y <= bounds.yMax; y += 2) {
        var coord = invert(x, y);

        if (coord) {
          var λ = coord[0],
              φ = coord[1];

          if (isFinite(λ)) {
            var heat = grid.interpolate(λ, φ);

            if (heat) {
              column[y + 1] = column[y] = heat;
            }
          }
        }
      }

      columns[x + 1] = columns[x] = column;
    }

    (function batchInterpolate() {
      var start = Date.now();

      while (x < bounds.width) {
        interpolateColumn(x);
        x += 2;

        if (Date.now() - start > 1000) {
          //MAX_TASK_TIME) {
          setTimeout(batchInterpolate, 25);
          return;
        }
      }

      createField(columns, bounds, callback);
    })();


  };





    var colorStyles = windIntensityColorScale(MIN_VELOCITY_INTENSITY, MAX_VELOCITY_INTENSITY);


    var g = params.canvas.getContext("2d");
    context = g
    g.lineWidth = PARTICLE_LINE_WIDTH;
    g.fillStyle = fadeFillStyle;
    g.globalAlpha = 0.6;



    function draw() {

      if (areCoordinatesDirty)
      {
          g.globalCompositeOperation = "copy";
          g.globalAlpha = 1;
          g.fillStyle = "rgba(0,0,0,0)";
          g.fillRect(bounds.x, bounds.y, bounds.width, bounds.height);
          areCoordinatesDirty = false;
          g.fillStyle = fadeFillStyle;
          return;

      }
      // Fade existing particle trails by painting a clear rectangle with some opacity.
      var prev = "lighter";
      g.globalCompositeOperation = "destination-in";
      g.fillRect(bounds.x, bounds.y, bounds.width, bounds.height);
      g.globalCompositeOperation = prev;
      g.globalAlpha = OPACITY === 0 ? 0 : OPACITY * 0.9; // Draw new particle trails.

      // Each bucket contains all sections with the same intensity (color). Why? Who knows...
      // These sections are called "particles", also for some reason.
      buckets.forEach(function (bucket, i) {
        if (bucket.length > 0) {
          g.beginPath();
          g.strokeStyle = colorStyles[i];
          bucket.forEach(function (particle) {
            g.moveTo(particle.x, particle.y);
            g.lineTo(particle.xt, particle.yt);
            particle.x = particle.xt;
            particle.y = particle.yt;
          });
          g.stroke();
        }
      });
    }

    var then = Date.now();



  };

  var start = function start(bounds, width, height, extent) {
    var mapBounds = {
      south: deg2rad(extent[0][1]),
      north: deg2rad(extent[1][1]),
      east: deg2rad(extent[1][0]),
      west: deg2rad(extent[0][0]),
      width: width,
      height: height
    };
    stop(); // build grid

    buildGrid(gridData, function (grid) {
      // interpolateField

      interpolateField(grid, buildBounds(bounds, width, height), mapBounds, function (bounds, field) {
        // animate the canvas with random points
        heat.field = field;

      });
    });
  };


  var heat = {
    params: params,
    start: start,
    stop: stop,
    createField: createField,
    interpolatePoint: interpolate,
    setData: setData,
    setOptions: setOptions
  };
  return heat;
};

