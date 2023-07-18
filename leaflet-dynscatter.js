"use strict";


var drawingCount = 0

// const pad = function(num, digits)
// // Converts an integer number into a string with the specified digits, pading with zeros from the left if necessary
// {
//     return ('00000000000000000' + num).slice(-digits);
// }



let loadScatterVarData = function loadScatterVarData(fileName, idxDate, varName, gridType) {
    let data = Array(1);
    let dimsData = 0;

    // Read the mesh.
    let dimsLat, lat, dimsLon, lon

    if (gridType[2]==32) {
        [dimsLat, lat] = window.loadBinaryDODSFloat32Cached(fileName + '?' + gridType[0]);
        [dimsLon, lon] = window.loadBinaryDODSFloat32Cached(fileName + '?' + gridType[1]);
    }
    else
    {
        [dimsLat, lat] = window.loadBinaryDODSFloat64Cached(fileName + '?' + gridType[0]);
        [dimsLon, lon] = window.loadBinaryDODSFloat64Cached(fileName + '?' + gridType[1]);
    }


    try
    {
        // const fullFileName = fileName + '?' + varName + '%5B' + (idxDate + 1) + '%5D%5B0:1:' + (dims[1] -1) + '%5D%5B0:1:' + (dims[0] -1) + '%5D';
        const fullFileName = fileName + '?' + varName + '%5B0:1:' + (lat.length -1)  + '%5D';
        [dimsData, data] = window.loadBinaryDODSFloat32Cached(fullFileName);
    }
    catch(err) {
        [dimsData, data] = [null, null]
    }

    return [lat, lon, data];
}



// const Cmap = class
// {
//     constructor(options, nLevels)
//     {
//         this.nLevels = nLevels;
//
//         this.R = Array(nLevels);
//         this.G = Array(nLevels);
//         this.B = Array(nLevels);
//
//         let cmap = options.cmap;
//         let cbar = options.cbar;
//         this.cmap = cmap;
//         this.cbar = cbar;
//
//
//         for (let i = 0; i < nLevels; i++)
//         {
//             const x = i/nLevels;
//
//             const idx = binSearch(cmap.stops, x);
//
//             const w = (x - cmap.stops[idx])/(cmap.stops[idx + 1] - cmap.stops[idx]);
//
//             this.R[i] = Math.round(255*((1 - w)*cmap.colors[idx][0] + w*cmap.colors[idx+1][0]));
//             this.G[i] = Math.round(255*((1 - w)*cmap.colors[idx][1] + w*cmap.colors[idx+1][1]));
//             this.B[i] = Math.round(255*((1 - w)*cmap.colors[idx][2] + w*cmap.colors[idx+1][2]));
//
//         }
//
//     }
//
//     colors(val)
//     {
//         const idx = Math.round((val - this.cbar.min)/(this.cbar.max - this.cbar.min)*this.nLevels);
//
//         return [this.R[idx], this.G[idx], this.B[idx]];
//
//     }
//
// }

function addNewDynScatterLayer(map, fileName, varName, gridType, cmap, cbar, varThresholdMin, varThresholdMax, visible)
// Creates and returns a dynamic heatmap map layer (CCS) based on the datafiles.
{

    // const dims = [ni, nj, nt];
    let [lat, lon, data] = loadScatterVarData(fileName, 0, varName, gridType)
    console.log("dajkdslkajdslakdjsal")


    // Creates the data structure.
    let layerData = {header: {parameterUnit: "m.s-1", parameterNumber: 2,
            parameterNumberName: "Eastward current", parameterCategory: 2,
            lat: lat,
            lon: lon,
            // times: times, dimsTime: dimsTime, timeFloatBytes: timeFloatBytes,
            // refTime: "2022-09-30 00:00:00",
            latLonSize: lat.length},
        data: data.slice(0, lat.length),
        varName: varName,
        fileName: fileName};


    // Creates the leaflet layer.
    let scatterLayer = L.createDynScatterLayer({
        displayValues: true,
        displayOptions: {
            velocityType: "Global Wind",
            position: "bottomright",
            emptyString: "sss No wind data",
        },
        data: layerData,
        visible: true,
        cmap: cmap,
        cbar: cbar,
        varThresholdMin: varThresholdMin,
        varThresholdMax: varThresholdMax,
    });

    return scatterLayer
}






L.createDynScatterLayer = function (options) {
    return new L.DynscatterLayer(options);
};

L.DynscatterLayer = L.Layer.extend({
    initialize: function initialize(options)
    {
        L.setOptions(this, options);


        this.fileName = options.data.fileName;
        this.varName  = options.data.varName;


        this.image = null
        this.indicesCache = null
        this.windowSizes = [0,0];



    },

    peekValue: function peekValue(lat, lon) {
        const data = this.dat;

        if (data != undefined) {
            // Computes the size of pixel in terms of lat, lon
            const pTL = this._map.containerPointToLatLng(L.point(0, 0))
            const pBR = this._map.containerPointToLatLng(L.point(1, 1))
            const D = 3*Math.max(pBR.lat - pTL.lat, pBR.lng - pTL.lng)

            for (let i = 0; i < data.length; i++)
            {
                if (Math.abs(lat - this.lat[i])<=D && Math.abs(lon - this.lon[i])<=D) {
                    return [data[i]];

                }

            }
            return [1e36];

        }
        else return [1e36];
    },

    onDateChange: function(idxDate)
    {
        this.idxDate = idxDate;

    },

    draw: function draw()
    {
        const data = this.dat;
        const lat  = this.lat;
        const lon  = this.lon;

        const W = this._container.width
        const H = this._container.height

        const g = this.g;

        g.clearRect(0, 0, W, H);


        drawingCount++;

        if (data != undefined) {
            for (let i = 0; i < data.length; i++)
            {
                const latlng = L.latLng(lat[i], lon[i]);
                const p = this._map.latLngToContainerPoint(latlng);

                if (p.x>-10 && p.y>-10) {
                    // Draw rectangle
                    const [R, G, B] = this.cmap.colors(data[i])

                    g.fillStyle = 'RGB('+ R.toString() + "," + G.toString() + "," + B.toString() + ")";
                    g.fillRect(p.x - 3, p.y - 3, 6, 6);

                }

            }

        }




        drawingCount--;


    },


    onAdd: function(map) {
        map.options.zoomAnimation = false;
        map.zoomControl.options.zoomAnimation = false;
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

        const data = this.options.data;
        this.lat = data.header.lat;
        this.lon = data.header.lon;
        this.dat = data.data;


        this.varScale = this.options.varScale;
        this.varThresholdMin = this.options.varThresholdMin;
        this.varThresholdMax = this.options.varThresholdMax;
        this.varThreshold    = this.options.varThreshold;

        this.g = this._container.getContext("2d");

        let topLeft = map.containerPointToLayerPoint([0, 0]);
        L.DomUtil.setPosition(this._container, topLeft);

        // this.draw();


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
        this.draw();



    },



});
