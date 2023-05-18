"use strict";


const pad = function(num, digits)
// Converts an integer number into a string with the specified digits, pading with zeros from the left if necessary
{
  return ('00000000000000000' + num).slice(-digits);
}


// Binary Search of the interval that contains x
var binSearch = function(arr, x) {

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


var UtoR = function(dims, data, isT)
// Interpolates an array of values defined on a U mesh into an R mesh
{

    if (isT) {
        const ndi = dims.sizes[1] - 1;
        const ndj = dims.sizes[2];
        const nsi = dims.sizes[1];
        const nsj = dims.sizes[2];
        let res = new Array(ndi * ndj);
        for (let i = 0; i < nsi - 1; i++) {
            for (let j = 0; j < nsj; j++) {
                // isT and isnT decide if the array is transposed or not.
                const idxSrc = (i*nsj + j);
                const idxDst = (i*ndj + j);
                // res[idxDst] = 0.5*(data[idxSrc] + data[idxSrc+1])
                res[idxDst] = data[idxSrc]
            }
            // const idxDst0   = (i + 0*ndi);
            // const idxDst1   = (i + 1*ndi);
            // const idxDstNm1 = (i + (nsj-1)*ndi);
            // const idxDstN   = (i + nsj*ndi);
            // res[idxDst0] = data[idxDst1]
            // res[idxDstN] = data[idxDstNm1]

        }
        return [ndi, ndj, res];
    }
    else
    {


    }
}

var VtoR = function(dims, data, isT)
// Interpolates an array of values defined on a U mesh into an R mesh
{
    if (isT) {
        const ndi = dims.sizes[1];
        const ndj = dims.sizes[2] - 1;
        const nsi = dims.sizes[1];
        const nsj = dims.sizes[2];
        let res = new Array(ndi * ndj);
        for (let j = 0; j < nsj; j++) {
            for (let i = 1; i < nsi; i++) {
                // isT and isnT decide if the array is transposed or not.
                const idxSrc = (i*nsj + j);
                const idxDst = (i*ndj + j);
                // res[idxDst] = 0.5*(data[idxSrc] + data[idxSrc+1])
                res[idxDst] = data[idxSrc]
            }
            // const idxDst0   = (j + 0*ndj);
            // const idxDst1   = (j + 1*ndj);
            // const idxDstNm1 = (j + (nsi-1)*ndj);
            // const idxDstN   = (j + nsi*ndj);
            // res[idxDst0] = data[idxDst1]
            // res[idxDstN] = data[idxDstNm1]

        }
        return [ndi, ndj, res];
    }
    else
    {


    }
    // const isNotT = 1 - isT
    // const ndi = dims.sizes[1] - isT;
    // const ndj = dims.sizes[2] - isNotT;
    // const nsi = dims.sizes[1];
    // const nsj = dims.sizes[2];
    // let res = new Array(ndi*ndj);
    // for (let i=0; i<ndi; i++)
    // {
    //     for (let j=0; j<ndj; j++)
    //     {
    //         // isT and isnT decide if the array is transposed or not.
    //         const idxSrc = isT*(i + j*nsi) + isNotT*(i*nsj + j);
    //         const idxDst = isT*(i + j*ndi) + isNotT*(i*ndj + j);
    //         // res[idxDst] = 0.5*(data[idxSrc] + data[idxSrc + isT*nsi + isNotT*nsj])
    //         res[idxDst] = data[idxSrc]
    //     }
    // }
    // return [ndi, ndj, res];
}
    // [dims, dataV] = VtoR(dimsDataV, dataV)


let loadGridData = function loadGridData(fileName, idxDate, gridType, timeVar, timeOffsettime, UnitsInSeconds) {
    // let fileName = `https://icoast.rc.ufl.edu/thredds/dodsC/matthew/L1_qck_${pad(year,4)}${pad(month,2)}${pad(day,2)}.nc.dods`;

    // Read the time dimension
    let [dimsTime, timesNC] = window.loadBinaryDODSFloat64Cached(fileName + '?' + timeVar);
    let times = [];

    // Converts the time into JavaScript
    for (let i = 0; i< timesNC.length; i++) {
        const time = (timesNC[i] + timeOffsettime)*UnitsInSeconds*1000;
        console.log('tt  ', time);
        times.push(time);
    }

    // Converts the time into 

    // Read the mesh.
    let [dimsLat, lat] = window.loadBinaryDODSFloat64Cached(fileName + '?' + gridType[0]);
    let [dimsLon, lon] = window.loadBinaryDODSFloat64Cached(fileName + '?' + gridType[1]);

    return [dimsTime, times, dimsLat, lat, dimsLon, lon];
}

let loadVarData = function loadVarData(fileName, idxDate, varName, dims) {
    let data = Array(1);
    let dimsData = 0;


    const fullFileName = fileName + '?' + varName + '%5B' + (idxDate + 1) + '%5D%5B0:1:' + (dims[1] -1) + '%5D%5B0:1:' + (dims[0] -1) + '%5D';
    [dimsData, data] = window.loadBinaryDODSFloat32Cached(fullFileName);


    return [dimsData, data];
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


        for (let i = 0; i < nLevels; i++)
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

function addNewDynHeatmapLayer(map, fileName, varName, gridType, timeVar, timeOffset, timeUnitsInSeconds, cmap, cbar)
// Creates and returns a dynamic heatmap map layer (CCS) based on the datafiles.
{
    const  [dimsTime, times, dimsLat, lat, dimsLon, lon] = loadGridData(fileName, 0, gridType, timeVar, timeOffset, timeUnitsInSeconds)


    // A general mesh is one that has different lat lon pairs for each node, i.e. lat and lon arrays are bidimensional.
    const isGeneralMesh = dimsLon.sizes.length > 1 && dimsLon.sizes[0] > 1 && dimsLon.sizes[1] > 1;
    let ni, nj = 0;
    if (isGeneralMesh) {
        ni = dimsLat.sizes[1];
        nj = dimsLat.sizes[0];
    }
    else {
        ni = lat.length;
        nj = lon.length;
    }
    const nt = times.length;

    const dims = [ni, nj, nt];
    let [dimsData, data] = loadVarData(fileName, 0, varName, dims)


    // Creates the data structure.
    let layerData = {header: {parameterUnit: "m.s-1", parameterNumber: 2,
            parameterNumberName: "Eastward current", parameterCategory: 2,
            lat: lat, dimsLat: dimsLat,
            lon: lon, dimsLon: dimsLat,
            times: times, dimsTime: dimsTime,
            refTime: "2022-09-30 00:00:00",
            latLonDims: dimsLon.sizes.length,
            latLonSize: dimsLon.sizes,},
            data: data.slice(0, ni*nj),
            varName: varName,
            fileName: fileName,
            dims: dims,
            isGeneralMesh: isGeneralMesh};


    // Creates the leaflet velocity layer.
    let heatmapLayer = L.createDynmapLayer({
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
    });

    return [heatmapLayer, times]
}



function addNewDynVectormapLayer(map, fileName, varNames, gridTypeU, gridTypeV, timeVar, timeOffset, timeUnitsInSeconds, cmap, cbar, varScale, varThreshold)
// Creates and returns a dynamic heatmap map layer (CCS) based on the datafiles.
{
    if (gridTypeU[0] !== gridTypeV[0]) {
        console.log('ERROR: gridTypes different from Rho are not yet supported.')
    }
    const  [dimsTime, times, dimsLat, lat, dimsLon, lon] = loadGridData(fileName, 0, gridTypeU, timeVar, timeOffset, timeUnitsInSeconds)

    // A general mesh is one that has different lat lon pairs for each node, i.e. lat and lon arrays are bidimensional.
    const isGeneralMesh = dimsLon.sizes.length > 1 && dimsLon.sizes[0] > 1 && dimsLon.sizes[1] > 1;
    let ni, nj = 0;
    if (isGeneralMesh) {
        ni = dimsLat.sizes[1];
        nj = dimsLat.sizes[0];
    }
    else {
        ni = lat.length;
        nj = lon.length;
    }
    const nt = times.length;

    const dims = [ni, nj, nt];

    let [dimsDataU, dataU] = loadVarData(fileName, 0, varNames[0], dims)
    let [dimsDataV, dataV] = loadVarData(fileName, 0, varNames[1], dims)

    // let ndi = 0,  ndj = 0;
    // let dataUR, dataVR, latR, lonR;
    // const isT = 1;
    // [ndi, ndj, dataUR] = UtoR(dimsDataU, dataU, isT);
    // [ndi, ndj, dataVR] = VtoR(dimsDataV, dataV, isT);
    // [ndi, ndj, latR]   = UtoR(dimsDataU, latU,  isT);  // Chose U to get the R latitude and longitude. Could've chosen V.
    // [ndi, ndj, lonR]   = UtoR(dimsDataU, lonU,  isT);
    // [ndi, ndj, latR]   = VtoR(dimsDataV, latV,  isT);  // Chose U to get the R latitude and longitude. Could've chosen V.
    // [ndi, ndj, lonR]   = VtoR(dimsDataV, lonV,  isT);
    // const dimsR = {names: dimsDataU.names, sizes: [ndi, ndj]};
    // const dims = [ndi, ndj, nt];

    // Creates the data structure.
    let layerData = {header: {parameterUnit: "m.s-1", parameterNumber: 2,
            parameterNumberName: "Eastward current", parameterCategory: 2,
            lat: lat, dimsLat: dims,
            lon: lon, dimsLon: dims,
            times: times, dimsTime: dimsTime,
            refTime: "2022-09-30 00:00:00",
            latLonDims: dimsLon.sizes.length,
            latLonSize: dimsLon.sizes,},
        dataU: dataU.slice(0, ni*nj),
        dataV: dataV.slice(0, ni*nj),
        varName: varNames,
        fileName: fileName,
        dims: dims,
        // dimsU: dimsU,
        // dimsV: dimsV,
        isGeneralMesh: isGeneralMesh};


    // Creates the leaflet velocity layer.
    let heatmapLayer = L.createDynmapLayer({
        displayValues: true,
        displayOptions: {
            velocityType: "Global Wind",
            position: "bottomright",
            emptyString: "sss No wind data",
        },
        data: layerData,
        varThreshold: varThreshold,
        varScale: varScale,
        visible: true,
        cmap: cmap,
        cbar: cbar,
    });
    return [heatmapLayer, times]
}


L.createDynmapLayer = function (options) {
    return new L.DynmapLayer(options);
};

L.DynmapLayer = L.Layer.extend({
    initialize: function initialize(options)
    {
        L.setOptions(this, options);

        // A general mesh is one that has different lat lon pairs for each node, i.e. lat and lon arrays are bidimensional.
        // this.isGeneralMesh = options.data.header.latLonDims > 1 && options.data.header.latLonSize[0] > 1 && options.data.header.latLonSize[1] > 1;
        //
        // if (this.isGeneralMesh) {
        //     this.ni = options.data.header.latLonSize[1];
        //     this.nj = options.data.header.latLonSize[0];
        // }
        // else {
        //     this.ni = this.options.data.header.lat.length;
        //     this.nj = this.options.data.header.lon.length;
        // }
        //
        // this.nt = this.options.data.header.dimsTime.size[0];

        this.isGeneralMesh = options.data.isGeneralMesh;
        [this.ni, this.nj, this.nt] = options.data.dims;

        this.fileName = options.data.fileName;
        this.varName  = options.data.varName;
        this.dims     = options.data.dims;
        this.dimsU    = options.data.dimsU;  // These two might not exist if it is a scalar var
        this.dimsV    = options.data.dimsV;



    },

    peekValue: function peekValue(lat, lon) {
        const isT = 1, isnT = 0;
        const ni = this.ni;
        const nj = this.nj;

        const TL = this._map.latLngToContainerPoint(this.pTL);
        const TR = this._map.latLngToContainerPoint(this.pTR);
        const BL = this._map.latLngToContainerPoint(this.pBL);
        const BR = this._map.latLngToContainerPoint(this.pBR);

        const xL = Math.max(0, Math.min(TL.x, TR.x, BL.x, BR.x));
        const yB = Math.max(0, Math.min(TL.y, TR.y, BL.y, BR.y));
        const xR = Math.min(this._container.width,  Math.max(TL.x, TR.x, BL.x, BR.x));
        const yT = Math.min(this._container.height, Math.max(TL.y, TR.y, BL.y, BR.y));


        const W = xR - xL + 1;
        const H = yT - yB + 1;
        if (W<=0 || H<=0) return;


        const M11 = this.M11;
        const M12 = this.M12;
        const M21 = this.M21;
        const M22 = this.M22;
        const O = this.O;

        const p = L.latLng(lat, lon);

        const p1 = L.latLng(M11 * (p.lat - O.lat) + M21 * (p.lng - O.lng), M12 * (p.lat - O.lat) + M22 * (p.lng - O.lng));

        if (p1.lat >= 0 && p1.lng >= 0 && p1.lat <= 1 && p1.lng <= 1 && this.options.data.data != undefined) {

            // transforms the point from the unit box to a rectangle of the proper size.
            p1.lat *= this.lat1d[ni - 1];
            p1.lng *= this.lon1d[nj - 1];

            const isT = 1, isnT = 0;

            const Slat = isT + (1 - isT) * nj;
            const Slon = isT * ni + (1 - isT);

            const iLat = binSearch(this.lat1d, p1.lat);
            const iLon = binSearch(this.lon1d, p1.lng);
            // console.log('eeee', iLat, iLon, lat, lon);
            // console.log(this.lat1d)
            // console.log(this.lon1d)
            // console.log('val: ', this.options.data.data[Slat * iLat + Slon * iLon]);
            return this.options.data.data[Slat * iLat + Slon * iLon];
        }
        else return NaN;
    },

    onDateChange: function(idxDate)
    {
        this.idxDate = idxDate
        console.log(4444, idxDate)
        if (typeof this.varName === 'string') {
            let [dimsData, data] = loadVarData(this.fileName, idxDate, this.varName, this.dims);

            this.options.data.data = data.slice(0, this.ni*this.nj);
        } else
        {
            let [dimsDataU, dataU] = loadVarData(this.fileName, idxDate, this.varName[0], this.dims);
            let [dimsDataV, dataV] = loadVarData(this.fileName, idxDate, this.varName[1], this.dims);

            this.options.data.dataU = dataU.slice(0, dimsDataU.sizes[1]*dimsDataU.sizes[2]);
            this.options.data.dataV = dataV.slice(0, dimsDataV.sizes[1]*dimsDataV.sizes[2]);
        }




    },

    draw: function draw()
    {
        const ni = this.ni;
        const nj = this.nj;

        const data = this.options.data;
        const lat = this.lat1d;
        const lon = this.lon1d;
        const dat  = data.data;
        const datU = data.dataU;
        const datV = data.dataV;

        const g = this.g;

        g.clearRect(0, 0, this._container.width, this._container.height);

        const TL = this._map.latLngToContainerPoint(this.pTL);
        const TR = this._map.latLngToContainerPoint(this.pTR);
        const BL = this._map.latLngToContainerPoint(this.pBL);
        const BR = this._map.latLngToContainerPoint(this.pBR);


        const xL = Math.max(0, Math.min(TL.x, TR.x, BL.x, BR.x));
        const yB = Math.max(0, Math.min(TL.y, TR.y, BL.y, BR.y));
        const xR = Math.min(this._container.width,  Math.max(TL.x, TR.x, BL.x, BR.x));
        const yT = Math.min(this._container.height, Math.max(TL.y, TR.y, BL.y, BR.y));


        const W = xR - xL + 1;
        const H = yT - yB + 1;
        if (W<=0 || H<=0) return;


        const M11 = this.M11;
        const M12 = this.M12;
        const M21 = this.M21;
        const M22 = this.M22;
        const O = this.O;

        const isT = 1, isnT = 0;


        const arr = new Uint8ClampedArray(4*W*H);
        let image = new ImageData(arr, W, H);

        const Slat = isT + (1 - isT)*nj;
        const Slon = isT*ni + (1 - isT);

        // Draws all the pixels one by one
        if (dat != undefined) {

            let idx = 0;
            for (let j = yB; j <= yT; j++) {
                for (let i = xL; i <= xR; i++) {
                    const p = this._map.containerPointToLatLng(L.point(i, j));

                    const p1 = L.latLng(M11 * (p.lat - O.lat) + M21 * (p.lng - O.lng), M12 * (p.lat - O.lat) + M22 * (p.lng - O.lng));

                    if (p1.lat >= 0 && p1.lng >= 0 && p1.lat <= 1 && p1.lng <= 1) {

                        // transforms the point from the unit box to a rectangle of the proper size.
                        p1.lat *= lat[ni - 1];
                        p1.lng *= lon[nj - 1];

                        const iLat = binSearch(lat, p1.lat);
                        const iLon = binSearch(lon, p1.lng);

                        const val = dat[Slat*iLat + Slon*iLon];

                        if (!isNaN(val) && val != 0 && val>-1.8 && val<1.8) {
                            const [R, G, B] = this.cmap.colors(val);

                            image.data[idx    ] = R;
                            image.data[idx + 1] = G;
                            image.data[idx + 2] = B;
                            image.data[idx + 3] = 255;
                        }
                    }

                    idx += 4;
                }
            }

            g.putImageData(image, xL, yB);


        }

        if (datU != undefined) {

            const arrowGridYSize = 14;
            const arrowGridXSize = 14;

            const scale = this.varScale;

            for (let j = yB; j <= yT; j += arrowGridYSize) {
                for (let i = xL; i <= xR; i += arrowGridXSize) {
                    const p = this._map.containerPointToLatLng(L.point(i, j));

                    const p1 = L.latLng(M11 * (p.lat - O.lat) + M21 * (p.lng - O.lng), M12 * (p.lat - O.lat) + M22 * (p.lng - O.lng));

                    if (p1.lat < 0 || p1.lng < 0 || p1.lat > 1 || p1.lng > 1) continue;

                    // transforms it from the unit box to a rectangle of the proper size.
                    p1.lat *= lat[ni - 1];
                    p1.lng *= lon[nj - 1];

                    const iLat = binSearch(lat, p1.lat);
                    const iLon = binSearch(lon, p1.lng);

                    // isT and isnT decide if the array is transposed or not.
                    const u = datU[Slat*iLat + Slon*iLon];
                    const v = datV[Slat*iLat + Slon*iLon];
                    const val = Math.sqrt(u*u + v*v);


                    if (!isNaN(val) && val != 0 && val<1) {
                        const [R, G, B] = this.cmap.colors(val);

                        const decColor = B + 0x100 * G + 0x10000 * R;
                        const color = '#' + decColor.toString(16);
                        g.fillStyle = color;

                        // // Finds unitary vector in the directions of U and V.
                        // const pU = destination(p,  0, 0.01);
                        // const pV = destination(p, 90, 0.01);
                        //
                        // // const dV = p.distanceTo(pV);
                        // // const dU = p.distanceTo(pU);
                        // const dU = Math.sqrt((pU.lat - p.lat) * (pU.lat - p.lat) + (pU.lng - p.lng) * (pU.lng - p.lng));
                        // const dV = Math.sqrt((pV.lat - p.lat) * (pV.lat - p.lat) + (pV.lng - p.lng) * (pV.lng - p.lng));
                        //
                        // const vU = [(pU.lat - p.lat) / dU, (pU.lng - p.lng) / dU];
                        // const vV = [(pV.lat - p.lat) / dV, (pV.lng - p.lng) / dV];
                        // // const a = Math.atan2(p2.lat - p.lat, p2.lng - p.lng)
                        //
                        // const ux = u * vU[0] + v * vV[0];
                        // const uy = u * vU[1] + v * vV[1];

                        const ux = u;
                        const uy = v;

                        // Draw the vectors.
                        g.beginPath();
                        g.moveTo(i, j);
                        g.lineTo(i + scale * (-0.05 * uy), j + scale * (0.05 * ux));
                        g.lineTo(i + scale * (-0.05 * uy + 0.6 * ux), j + scale * (0.05 * ux + 0.6 * uy));
                        g.lineTo(i + scale * (-0.2 * uy + 0.6 * ux), j + scale * (0.2 * ux + 0.6 * uy));
                        g.lineTo(i + scale * (ux), j + scale * (uy));
                        g.lineTo(i + scale * (0.2 * uy + 0.6 * ux), j + scale * (-0.2 * ux + 0.6 * uy));
                        g.lineTo(i + scale * (0.05 * uy + 0.6 * ux), j + scale * (-0.05 * ux + 0.6 * uy));
                        g.lineTo(i + scale * (0.05 * uy), j + scale * (-0.05 * ux));


                        g.closePath();
                        g.fill();
                    }
                }
            }
        }

        // Draw rectangle
        g.beginPath();
        const aTL = this._map.latLngToContainerPoint(this.pTL);
        const aTR = this._map.latLngToContainerPoint(this.pTR);
        const aBL = this._map.latLngToContainerPoint(this.pBL);
        const aBR = this._map.latLngToContainerPoint(this.pBR);
        g.moveTo(aTL.x, aTL.y);
        g.lineTo(aTR.x, aTR.y);
        g.lineTo(aBR.x, aBR.y);
        g.lineTo(aBL.x, aBL.y);
        g.lineTo(aTL.x, aTL.y);
        g.stroke();


        // if (this._timer) clearTimeout(self._timer);
        // this._timer = setTimeout((function  () {
        //     this.onDateChange(this.idxDate+1)
        //     this.draw();
        //
        // }).bind(this), 10); // showing velocity is delayed. JMG: why? (used to be 750)

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

        const ni = this.ni;
        const nj = this.nj;

        const data = this.options.data;
        this.lat = data.header.lat;
        this.lon = data.header.lon;
        this.dat = data.data;

        if (this.isGeneralMesh) {
            let Si = 1, Sj = 1;
            const isT = 1;
            if (isT == 0) Si = nj;
            else          Sj = ni;

            // const iTL = 0*ni + 0;
            // const iTR = 0*ni + (ni-1);
            // const iBL = (nj-1)*ni + 0;
            // const iBR = (nj-1)*ni + (ni-1);
            const iTL = 0*Sj + 0*Si;
            const iTR = 0*Sj + (ni-1)*Si;
            const iBL = (nj-1)*Sj + 0*Si;
            const iBR = (nj-1)*Sj + (ni-1)*Si;


            this.pTL = L.latLng(this.lat[iTL], this.lon[iTL]);
            this.pTR = L.latLng(this.lat[iTR], this.lon[iTR]);
            this.pBL = L.latLng(this.lat[iBL], this.lon[iBL]);
            this.pBR = L.latLng(this.lat[iBR], this.lon[iBR]);

            // Computes 1D of array of "lat" and "lon" (in fact, degree "distances" from the origin along each axis).
            this.lat1d = Array(ni);
            this.lon1d = Array(nj);
            for (let i = 0; i<ni; i++)
            {
                const idx = 0*ni + i;
                this.lat1d[i] = Math.sqrt((this.pTL.lat - this.lat[idx])*(this.pTL.lat - this.lat[idx]) +
                                          (this.pTL.lng - this.lon[idx])*(this.pTL.lng - this.lon[idx]));
            }
            for (let j = 0; j<nj; j++)
            {
                const idx = j*ni + 0;
                this.lon1d[j] = Math.sqrt((this.pTL.lat - this.lat[idx])*(this.pTL.lat - this.lat[idx]) +
                                             (this.pTL.lng - this.lon[idx])*(this.pTL.lng - this.lon[idx]));
            }
        }
        else
        {
            this.pTL = L.latLng(this.lat[0],           this.lon[0]);
            this.pBL = L.latLng(this.lat[0],           this.lon[this.nj - 1]);
            this.pTR = L.latLng(this.lat[this.ni - 1], this.lon[0]);
            this.pBR = L.latLng(this.lat[this.ni - 1], this.lon[this.nj - 1]);

            this.lat1d = Array(ni);
            this.lon1d = Array(nj);
            for (let i = 0; i<ni; i++) this.lat1d[i] = this.lat[i] - this.lat[0];
            for (let j = 0; j<nj; j++) this.lon1d[j] = this.lon[j] - this.lon[0];
        }

        // Base vectors and origin for the mesh.
        const vX = L.latLng(this.pTR.lat - this.pTL.lat, this.pTR.lng - this.pTL.lng);
        const vY = L.latLng(this.pBL.lat - this.pTL.lat, this.pBL.lng - this.pTL.lng);
        this.O   = L.latLng(this.pTL.lat, this.pTL.lng);


        // Computes the inverse matrix M that transforms from a (lat,lng) point into a point in the unit mesh (0,1)x(0,1),
        const invDet = 1/(vX.lat*vY.lng - vX.lng*vY.lat);
        this.M11 =   invDet*vY.lng;
        this.M12 =  -invDet*vX.lng;
        this.M21 =  -invDet*vY.lat;
        this.M22 =   invDet*vX.lat;


        // this.scale = 12;
        this.varScale = this.options.varScale;
        this.varThreshold = this.options.varThreshold;

        this.g = this._container.getContext("2d");

        let topLeft = map.containerPointToLayerPoint([0, 0]);
        L.DomUtil.setPosition(this._container, topLeft);

        this.draw();

        // var self = this;
        // setTimeout(function () {
        //     self._onLayerDidMove();
        // }, 0);

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
