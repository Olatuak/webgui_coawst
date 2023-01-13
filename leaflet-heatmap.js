"use strict";


// Binary Search of the interval that contains x
var binSearch = function (arr, x) {

    let L = 0
    let R = arr.length-1;

    // Iterate until the value is found
    while (R-L > 1)
    {
        // Find the mid index
        let M = (L + R) >> 1;

        if (arr[M] < x)
             L = M;
        else
             R = M;
    }

    return L;
}


const Cmap = class
{
    constructor(options, nLevels)
    {
        this.nLevels = nLevels;

        this.R = Array(nLevels);
        this.G = Array(nLevels);
        this.B = Array(nLevels);

        var cmap = options.cmap;
        var cbar = options.cbar;
        this.cmap = cmap;
        this.cbar = cbar;


        for (var i = 0; i < nLevels; i++)
        {
            var x = i/nLevels;

            idx = binSearch(cmap.stops, x);

            var w = (x - cmap.stops[idx])/(cmap.stops[idx + 1] - cmap.stops[idx]);

            this.R[i] = Math.round(255*((1 - w)*cmap.colors[idx][0] + w*cmap.colors[idx+1][0]));
            this.G[i] = Math.round(255*((1 - w)*cmap.colors[idx][1] + w*cmap.colors[idx+1][1]));
            this.B[i] = Math.round(255*((1 - w)*cmap.colors[idx][2] + w*cmap.colors[idx+1][2]));

        }

    }

    colors(val)
    {
        var idx = Math.round((val - this.cbar.min)/(this.cbar.max - this.cbar.min)*this.nLevels);

        return [this.R[idx], this.G[idx], this.B[idx]];

    }

}


L.createHeatmapLayer = function (options) {
  return new L.heatmapLayer(options);
};

L.heatmapLayer = L.Layer.extend({
    initialize: function initialize(options)
    {
        L.setOptions(this, options);

        this._map.options.zoomAnimation = true;
    },

    draw1: function draw1()
    {
        var ni = this.options.data.header.lon.length;
        var nj = this.options.data.header.lat.length;

        var pTL = [this.options.data.header.lat[0],    this.options.data.header.lon[0]];
        var pBR = [this.options.data.header.lat[nj-1], this.options.data.header.lon[ni-1]];

        var TL = this._map.latLngToContainerPoint(L.latLng(pTL[0], pTL[1]));
        var BR = this._map.latLngToContainerPoint(L.latLng(pBR[0], pBR[1]));


        var xL = Math.max(0, TL.x);
        var yB = Math.max(0, BR.y);
        var xR = Math.min(this._container.width,  BR.x);
        var yT = Math.min(this._container.height, TL.y);

//        this._map.invalidateSize();

        var data = this.options.data;
        var lat = data.header.lat;
        var lon = data.header.lon;
        var dat = data.data;

        var cmap = this.options.cmap;
        var cbar = this.options.cbar;


        var g = this._container.getContext("2d");
        g.clearRect(0, 0, this._container.width, this._container.height);
        var image = g.getImageData(xL, yB, xR - xL + 1, yT - yB + 1);

        // Draws all the pixels one by one
        var idx = 0;
        for (var j = yB; j<=yT; j++)
        {
            for (var i = xL; i<=xR; i++)
            {
                var p = this._map.containerPointToLatLng(L.point(i, j));

                var iLat = binSearch(lat, p.lat);
                var iLon = binSearch(lon, p.lng);

                var val = dat[iLat*data.header.lon.length + iLon];

                if (!isNaN(dat[iLat*data.header.lon.length + iLon]))
                {
                    var [R, G, B] = this.cmap.colors(val);

                    image.data[idx  ] = R; //200*Math.abs(val); //j % 256;
                    image.data[idx+1] = G;//i % 256;
                    image.data[idx+2] = B;
                    image.data[idx+3] = 255;
                }


                idx += 4;
            }
        }

        g.putImageData(image, xL, yB);
    },

    onAdd: function(map) {
        var pane = map.getPane(this.options.pane);
        this._container = L.DomUtil.create("canvas", "leaflet-layer");
        this._container.width = 1000;
        this._container.height = 800;
        this.pane = pane;

        pane.appendChild(this._container);


        map.on('zoomend viewreset', this._update, this);
        map.on('moveend', this._onLayerDidMove, this);

        this.cmap = new Cmap(this.options, 100);
    },

    onRemove: function(map) {
        this._container.remove();
        map.off('zoomend viewreset', this._update, this);
    },

    _update: function() {
        // Recalculate position of container

//        L.DomUtil.setPosition(this._container, point);

        // Add/remove/reposition children elements if needed
    },

    _onLayerDidResize: function _onLayerDidResize(resizeEvent) {

    },

   _onLayerDidMove: function _onLayerDidMove() {

        // Resets the location of the layer (this avoids some strange bugs).
        var topLeft = this._map.containerPointToLayerPoint([0, 0]);
        L.DomUtil.setPosition(this._container, topLeft);


//this.options.data.header.dimsLat

        this.draw1();

//        var ni = this.options.data.header.lon.length;
//        var nj = this.options.data.header.lat.length;
//
//        var pTL = [this.options.data.header.lat[0],    this.options.data.header.lon[0]];
//        var pBR = [this.options.data.header.lat[nj-1], this.options.data.header.lon[ni-1]];
//
//        var TL = this._map.latLngToContainerPoint(L.latLng(pTL[0], pTL[1]));
//        var BR = this._map.latLngToContainerPoint(L.latLng(pBR[0], pBR[1]));
//
//
//        var xL = Math.max(0, TL.x);
//        var yB = Math.max(0, BR.y);
//        var xR = Math.min(this._container.width,  BR.x);
//        var yT = Math.min(this._container.height, TL.y);
//
////        this._map.invalidateSize();
//
//        var data = this.options.data;
//        var lat = data.header.lat;
//        var lon = data.header.lon;
//        var dat = data.data;
//
//        var cmap = this.options.cmap;
//        var cbar = this.options.cbar;
//
//
//        var g = this._container.getContext("2d");
//        g.clearRect(0, 0, this._container.width, this._container.height);
//        var image = g.getImageData(xL, yB, xR - xL + 1, yT - yB + 1);
//
//        // Draws all the pixels one by one
//        var idx = 0;
//        for (var j = yB; j<=yT; j++)
//        {
//            for (var i = xL; i<=xR; i++)
//            {
//                var p = this._map.containerPointToLatLng(L.point(i, j));
//
//                var iLat = binSearch(lat, p.lat);
//                var iLon = binSearch(lon, p.lng);
//
//                var val = dat[iLat*data.header.lon.length + iLon];
//
//                if (!isNaN(dat[iLat*data.header.lon.length + iLon]))
//                {
//                    var [R, G, B] = this.cmap.colors(val);
//
//                    image.data[idx  ] = R; //200*Math.abs(val); //j % 256;
//                    image.data[idx+1] = G;//i % 256;
//                    image.data[idx+2] = B;
//                    image.data[idx+3] = 255;
//                }
//
//
//                idx += 4;
//            }
//        }
//
//        g.putImageData(image, xL, yB);


    },



});
