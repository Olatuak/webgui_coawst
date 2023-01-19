"use strict";


// Binary Search of the interval that contains x
var binSearch = function (arr, x) {

    let L = 0
    let R = arr.length-1;

    // Iterate until the value is found
    while (R-L > 1)
    {
        // Find the middle index
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

        let cmap = options.cmap;
        let cbar = options.cbar;
        this.cmap = cmap;
        this.cbar = cbar;


        for (var i = 0; i < nLevels; i++)
        {
            const x = i/nLevels;

            const idx = binSearch(cmap.stops, x);

            const w = (x - cmap.stops[idx])/(cmap.stops[idx + 1] - cmap.stops[idx]);

            this.R[i] = Math.round(255*((1 - w)*cmap.colors[idx][0] + w*cmap.colors[idx+1][0]));
            this.G[i] = Math.round(255*((1 - w)*cmap.colors[idx][1] + w*cmap.colors[idx+1][1]));
            this.B[i] = Math.round(255*((1 - w)*cmap.colors[idx][2] + w*cmap.colors[idx+1][2]));

        }

    }

    colors(val)
    {
        let idx = Math.round((val - this.cbar.min)/(this.cbar.max - this.cbar.min)*this.nLevels);

        return [this.R[idx], this.G[idx], this.B[idx]];

    }

}


L.createHeatmapLayer = function (options) {
  return new L.HeatmapLayer(options);
};

L.HeatmapLayer = L.Layer.extend({
    initialize: function initialize(options)
    {
        L.setOptions(this, options);

        // this._map.options.zoomAnimation = true;
    },

    draw1: function draw1()
    {
        const ni = this.options.data.header.lon.length;
        const nj = this.options.data.header.lat.length;

        const pTL = [this.options.data.header.lat[0],    this.options.data.header.lon[0]];
        const pBR = [this.options.data.header.lat[nj-1], this.options.data.header.lon[ni-1]];

        const TL = this._map.latLngToContainerPoint(L.latLng(pTL[0], pTL[1]));
        const BR = this._map.latLngToContainerPoint(L.latLng(pBR[0], pBR[1]));


        const xL = Math.max(0, TL.x);
        const yB = Math.max(0, BR.y);
        const xR = Math.min(this._container.width,  BR.x);
        const yT = Math.min(this._container.height, TL.y);


        const data = this.options.data;
        const lat = data.header.lat;
        const lon = data.header.lon;
        const dat = data.data;

        let g = this._container.getContext("2d");
        g.clearRect(0, 0, this._container.width, this._container.height);

        const W = xR - xL + 1;
        const H = yT - yB + 1
        if (W<=0 || H<=0) return;

        const arr = new Uint8ClampedArray(4*W*H);
        let image = new ImageData(arr, W, H);

        // Draws all the pixels one by one
        let idx = 0;
        for (let j = yB; j<=yT; j++)
        {
            for (let i = xL; i<=xR; i++)
            {
                const p = this._map.containerPointToLatLng(L.point(i, j));

                const iLat = binSearch(lat, p.lat);
                const iLon = binSearch(lon, p.lng);

                const val = dat[iLat*data.header.lon.length + iLon];

                if (!isNaN(val))
                {
                    const [R, G, B] = this.cmap.colors(val);

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

    // _animateZoom: function _animateZoom(e) {
    //     var scale = this._map.getZoomScale(e.zoom); // -- different calc of offset in leaflet 1.0.0 and 0.0.7 thanks for 1.0.0-rc2 calc @jduggan1
    //
    //
    //     var offset = L.Layer ? this._map._latLngToNewLayerPoint(this._map.getBounds().getNorthWest(), e.zoom, e.center) : this._map._getCenterOffset(e.center)._multiplyBy(-scale).subtract(this._map._getMapPanePos());
    //     // L.DomUtil.setTransform(this._canvas, offset, scale);
    //
    //     console.log("kkkkaaksskakask", scale);
    // },


    onAdd: function(map) {
        map.options.zoomAnimation = true;
        map.zoomControl.options.zoomAnimation = true;
        L.Browser.any3d = true;

        let pane = map.getPane(this.options.pane);
        this._container = L.DomUtil.create("canvas", "leaflet-layer");
        this._container.width = 1000;
        this._container.height = 800;
        this.pane = pane;
        L.DomUtil.addClass(this._container, "leaflet-zoom-hide");
        pane.appendChild(this._container);


        map.on('zoomend viewreset', this._update, this);
        map.on('moveend', this._onLayerDidMove, this);


        this.cmap = new Cmap(this.options, 100);

        this.draw1();
    },

    onRemove: function(map) {

        this.pane.removeChild(this._container);
        // this.remove();
        map.off('zoomend viewreset', this._update, this);
        map.off('moveend', this._onLayerDidMove, this);
    },

    _update: function(event) {
        // let map = event.target;
    },

    _onLayerDidResize: function _onLayerDidResize(resizeEvent) {

    },

   _onLayerDidMove: function _onLayerDidMove(event) {

        // Resets the location of the layer (this avoids some strange bugs).
        let map = event.target;
        this._map = map;
        let topLeft = map.containerPointToLayerPoint([0, 0]);
        L.DomUtil.setPosition(this._container, topLeft);

        // map.addLayer(this);
        this.draw1();

    },



});
