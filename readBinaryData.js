let cache = new Map();
let totCache = 0;
let keyCount = 0;


// function createUniqueKey()
// {
//     keyCount++;
//
//     return 'k' + keyCount;
// }

function getCachedVar(key)
{
    return cache.get(key);
}


function syncReq(file, encoding) {
    var xhr = new XMLHttpRequest();
    var exit = false;
    xhr.open('GET', file);
    // Using 'arraybuffer' as the responseType ensures that the raw data is returned,
    // rather than letting XMLHttpRequest decode the data first.
    xhr.responseType = 'arraybuffer';
    xhr.onload = function() {
        if (this.status == 200) {
            // The decode() method takes a DataView as a parameter, which is a wrapper on top of the ArrayBuffer.
            var dataView = new DataView(this.response);
            // The TextDecoder interface is documented at http://encoding.spec.whatwg.org/#interface-textdecoder
            // var decoder = new TextDecoder(encoding);
            // var decodedString = decoder.decode(dataView);
            // Add the decoded file's text to the <pre> element on the page.
        } else {
            console.error('Error while requesting', file, this);
        }
        exit = true;
    };
    xhr.send();

    // while (!exit) {};
}

function readDODSHeader(url)
// Read the ASCII header of the otherwise binary dods file.
{
    let res = [];
    let str  = [];

    let a = syncReq(url, "");

    let req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.overrideMimeType('text\/plain; charset=x-user-defined');
    req.send(null);


    if (req.status > 299) return byteArray;


    // The binary data starts after some ascii data that ends in 'Data:'
    let foundData = false;
    for (let i = 0; i < req.responseText.length-5; ++i)
    {
        if (req.responseText.slice(i,i+5) == 'Data:')
        {
            foundData = true;
            idx = i + 14
            break;
        }
    }

    // Error condition
    if (!foundData)
    {
      console.log('ERROR in file url. Data not found')
      return -1
    }

    let dims = {'names': [], 'sizes': []};

    // obtains the dimensions
    let header = req.responseText.slice(1, idx)
    while (header.indexOf('[') > -1)
    {
        var i1 = header.indexOf('[');
        var i2 = header.indexOf('=');
        var i3 = header.indexOf(']');
        var dimName = header.slice(i1+1, i2).trim();
        var dimSize = parseInt(header.slice(i2+1, i3).trim());

        dims['names'].push(dimName);
        dims['sizes'].push(dimSize);

        header = header.slice(i3+1, 1000000);


    }

    return [dims, req.responseText.slice(idx, -1)]
}


function loadBinaryDODSFloat32Cached(url)
{
    let res = getCachedVar(url);

    if (res == undefined) res = loadBinaryDODSFloat32ToCache(url);

    return res;

}

function loadBinaryDODSFloat64Cached(url)
{
    let res = getCachedVar(url);

    if (res == undefined) res = loadBinaryDODSFloat64ToCache(url);

    return res;
}

function loadBinaryDODSFloat32ToCache(url)
{
    let data = loadBinaryDODSFloat32(url);

    cache.set(url, data);

    totCache += data[1].length * 4;

    document.getElementById('txtCache').textContent = `${(totCache/1024/1024).toFixed(1)} mb`;


    return data;
}

function loadBinaryDODSFloat64ToCache(url)
{
    let data = loadBinaryDODSFloat64(url);

    cache.set(url, data);

    totCache += data[1].length * 8;
    document.getElementById('txtCache').textContent = `${(totCache/1024/1024).toFixed(1)} mb`;

    return data;
}

function loadBinaryDODSFloat32(url)
// Read a Thredds dods binary file of float32 as an array of bytes
// WARNING: Assumes little endian IEEE754
{
    let [dims, responseText] = readDODSHeader(url)
    res = [];

    // This is like a "union", fourU8 and oneF32 are two different views of the same buffer.
    buf = new ArrayBuffer(4);
    fourU8 = new Uint8Array(buf);
    oneF32 = new Float32Array(buf);

    // Reads the rest of bytes as Float32
    for (var i = 0; i < responseText.length; i+=4)
    {
        fourU8[0] = responseText.charCodeAt(i+3) & 0xff;
        fourU8[1] = responseText.charCodeAt(i+2) & 0xff;
        fourU8[2] = responseText.charCodeAt(i+1) & 0xff;
        fourU8[3] = responseText.charCodeAt(i  ) & 0xff;
        if (true) //(!isNaN(oneF32))
        {
            res.push(1.0*oneF32)
        }
        else
        {
            res.push(null)
        }
    }

    return [dims, new Float32Array(res)];
}

function loadBinaryDODSFloat64(url)
// Read a Thredds dods binary of float64 file as an array of bytes.
// WARNING: Assumes little endian IEEE754
{
    let [dims, responseText] = readDODSHeader(url);

    res = [];

    // This is like a "union", eightU8 and oneF64 are two different views of the same buffer.
    buf = new ArrayBuffer(8);
    eightU8 = new Uint8Array(buf);
    oneF64 = new Float64Array(buf);

    buf2 = new ArrayBuffer((responseText.length+1)/2);
    resF32 = new Float32Array(buf2);
    // Reads the rest of bytes as Float64
    for (let i = 0; i < responseText.length; i+=8)
    {
        eightU8[0] = responseText.charCodeAt(i+7) & 0xff;
        eightU8[1] = responseText.charCodeAt(i+6) & 0xff;
        eightU8[2] = responseText.charCodeAt(i+5) & 0xff;
        eightU8[3] = responseText.charCodeAt(i+4) & 0xff;
        eightU8[4] = responseText.charCodeAt(i+3) & 0xff;
        eightU8[5] = responseText.charCodeAt(i+2) & 0xff;
        eightU8[6] = responseText.charCodeAt(i+1) & 0xff;
        eightU8[7] = responseText.charCodeAt(i  ) & 0xff;

        // res.push(1.0*oneF64);
        resF32[i/8] = 1.0*oneF64
    }

    return [dims, resF32];
}


// function addNewHeatMap(map)
// {
//     // Reads the files/urls
//     lon  = loadBinaryDODSFloat64('./lon.bin')
//     lat  = loadBinaryDODSFloat64('./lat.bin')
//
//     var Nx = lon.length
//     var Ny = lat.length
//
//     inputData = loadBinaryDODSFloat32('./sample2.bin').slice(0, Nx*Ny)
//
//     var arr = []; // Initialize array
//     var k = 0
//     for (var j = 0 ; j < Ny; j++) {
//         arr[j] = []; // Initialize inner array
//         for (var i = 0; i < Nx; i++) {
//             arr[j][i] = inputData[k]
//             k++;
//         }
//     }
//
//     var data = [{
//       z: arr,
//       x: lon,
//       y: lat,
//       zsmooth: 'best',
//       type: 'heatmap',
//       hoverongaps: false,
//       connectgaps: false,
//       showscale: false,
//               colorscale:  [
//     ['0.0',            'rgb(165,0,38)'],
//     ['0.111111111111', 'rgb(215,48,39)'],
//     ['0.222222222222', 'rgb(244,109,67)'],
//     ['0.333333333333', 'rgb(253,174,97)'],
//     ['0.444444444444', 'rgb(254,224,144)'],
//     ['0.555555555556', 'rgb(224,243,248)'],
//     ['0.666666666667', 'rgb(171,217,233)'],
//     ['0.777777777778', 'rgb(116,173,209)'],
//     ['0.888888888889', 'rgb(69,117,180)'],
//     ['1.0',            'rgb(49,54,149)']
//   ],
//
//     }];

//
//     // Gives an id to the basemap, so Plotly can create the plot on top
//     mapid = document.getElementById('mapid');
//     baseMap = mapid.childNodes[0].childNodes[0]
//     baseMap.id = 'baseMapId'  // Warning, assuming many things
//
//
//     var layout = {
//
//         xaxis: {range: [Math.min(...lon), Math.max(...lon)], visible: false, fixedrange: true},
//         yaxis: {range: [Math.min(...lat), Math.max(...lat)], visible: false, fixedrange: true},
//
//         height: map._size.y,
//         width:  map._size.x,
//         margin: {pad: 0, border:0,l:0, r:0, t:0, b:0, autoexpand:true},
//         paper_bgcolor: "#00000000",
//         plot_bgcolor: "#00000000",
//
//
//
//     };
//
//
//
//     Plotly.newPlot('baseMapId', data, layout);
//
//
// }

// REMOVE
// function clearHeatmap(heatmapId)
// {
//
// }


// function updateHeatmap(heatmapId, mapLayer)
// // Ensures that a plotly layer is located in the right position
// {
//     try
//     {
//         bounds = mapLayer.getBounds()
//
//         update = {'xaxis': {'range': [bounds.getWest(),  bounds.getEast()],  'visible': false, 'fixedrange': true},
//                   'yaxis': {'range': [bounds.getSouth(), bounds.getNorth()], 'visible': false, 'fixedrange': true}}
//         window.Plotly.relayout(heatmapId, update)
//     }
//     catch(e)
//     {}
// }




