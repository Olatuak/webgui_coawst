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


var destination = function(latlng, heading, distance) {
    heading = (heading + 360) % 360;
    const rad = Math.PI / 180,
        radInv = 180 / Math.PI,
        R = 6378137, // approximation of Earth's radius
        lon1 = latlng.lng * rad,
        lat1 = latlng.lat * rad,
        rheading = heading * rad,
        sinLat1 = Math.sin(lat1),
        cosLat1 = Math.cos(lat1),
        cosDistR = Math.cos(distance / R),
        sinDistR = Math.sin(distance / R),
        lat2 = Math.asin(sinLat1 * cosDistR + cosLat1 *
            sinDistR * Math.cos(rheading))
    let lon2 = lon1 + Math.atan2(Math.sin(rheading) * sinDistR *
        cosLat1, cosDistR - sinLat1 * Math.sin(lat2));
    lon2 = lon2 * radInv;
    lon2 = lon2 > 180 ? lon2 - 360 : lon2 < -180 ? lon2 + 360 : lon2;
    return L.latLng([lat2 * radInv, lon2]);
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

    drawQuiver: function drawQuiver()
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

        const scale = 12;

        let g = this._container.getContext("2d");
        g.clearRect(0, 0, this._container.width, this._container.height);

        const W = xR - xL + 1;
        const H = yT - yB + 1
        if (W<=0 || H<=0) return;

        // const arr = new Uint8ClampedArray(4*W*H);
        // let image = new ImageData(arr, W, H);

        // Draws all the pixels one by one
        let idx = 0;
        const arrowGridYSize = 14;
        const arrowGridXSize = 14;

        for (let j = yB; j<=yT; j += arrowGridYSize)
        {
            for (let i = xL; i<=xR; i += arrowGridXSize)
            {
                const p = this._map.containerPointToLatLng(L.point(i, j));

                const iLat = binSearch(lat, p.lat);
                const iLon = binSearch(lon, p.lng);

                const val = dat[iLat*data.header.lon.length + iLon];
                const u = val;
                const v = 1 - val;

                if (!isNaN(val))
                {
                    const [R, G, B] = this.cmap.colors(val);

                    // image.data[idx  ] = R; //200*Math.abs(val); //j % 256;
                    // image.data[idx+1] = G;//i % 256;
                    // image.data[idx+2] = B;
                    // image.data[idx+3] = 255;

                    const decColor = B + 0x100 * G + 0x10000 * R ;
                    const color =  '#'+decColor.toString(16);
                    g.fillStyle = color;

                    // Finds unitary vector in the directions of U and V.
                    const pU = destination(p, 90, 0.01);
                    const pV = destination(p, 0,  0.01);

                    // const dV = p.distanceTo(pV);
                    // const dU = p.distanceTo(pU);
                    const dU = Math.sqrt((pU.lat - p.lat)*(pU.lat - p.lat) + (pU.lng - p.lng)*(pU.lng - p.lng));
                    const dV = Math.sqrt((pV.lat - p.lat)*(pV.lat - p.lat) + (pV.lng - p.lng)*(pV.lng - p.lng));

                    const vU = [(pU.lat - p.lat)/dU, (pU.lng - p.lng)/dU];
                    const vV = [(pV.lat - p.lat)/dV, (pV.lng - p.lng)/dV];
                    // const a = Math.atan2(p2.lat - p.lat, p2.lng - p.lng)

                    const ux = u*vU[0] + v*vV[0];
                    const uy = u*vU[1] + v*vV[1];



                    // Draw the vectors.
                    g.beginPath();
                    g.moveTo(i, j);
                    g.lineTo(i + scale*(-0.05*uy),          j + scale*( 0.05*ux));
                    g.lineTo(i + scale*(-0.05*uy + 0.6*ux), j + scale*( 0.05*ux + 0.6*uy));
                    g.lineTo(i + scale*( -0.2*uy + 0.6*ux), j + scale*(  0.2*ux + 0.6*uy));
                    g.lineTo(i + scale*(ux),                j + scale*(uy));
                    g.lineTo(i + scale*(  0.2*uy + 0.6*ux), j + scale*( -0.2*ux + 0.6*uy));
                    g.lineTo(i + scale*( 0.05*uy + 0.6*ux), j + scale*(-0.05*ux + 0.6*uy));
                    g.lineTo(i + scale*( 0.05*uy),          j + scale*(-0.05*ux));


                    g.closePath();
                    // g.lineTo(i + scale*(u*vU[0] + v*vV[0]), j + scale*(u*vU[1] + v*vV[1]));
                    g.fill();
                }

                idx += 4*arrowGridXSize;

            }

            idx += 4*(arrowGridYSize - 1)*W;
        }

        // g.putImageData(image, xL, yB);

    },


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

        this.drawQuiver();
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
        this.drawQuiver();

    },



});
