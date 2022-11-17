function readDODSHeader(url)
// Read the ASCII header of the otherwise binary dods file.
{
    var res = [];
    var str  = [];
    var req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.overrideMimeType('text\/plain; charset=x-user-defined');
    req.send(null);

    if (req.status != 200) return byteArray;

    // The binary data starts after some ascii data that ends in 'Data:'
    foundData = false;
    for (var i = 0; i < req.responseText.length-5; ++i)
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

    return req.responseText.slice(idx, -1)
}


function loadBinaryDODSFloat32(url)
// Read a Thredds dods binary file of float32 as an array of bytes
// WARNING: Assumes little endian IEEE754
{
    responseText = readDODSHeader(url)
    res = []

    // This is like a "union", fourU8 and oneF32 are two different views of the same buffer.
    buf = new ArrayBuffer(4);
    fourU8 = new Uint8Array(buf)
    oneF32 = new Float32Array(buf)

    // Reads the rest of bytes as Float32
    for (var i = 0; i < responseText.length; i+=4)
    {
        fourU8[0] = responseText.charCodeAt(i+3) & 0xff
        fourU8[1] = responseText.charCodeAt(i+2) & 0xff
        fourU8[2] = responseText.charCodeAt(i+1) & 0xff
        fourU8[3] = responseText.charCodeAt(i  ) & 0xff
        if (true) //(!isNaN(oneF32))
        {
            res.push(1.0*oneF32)
        }
        else
        {
            res.push(null)
        }
    }

    return new Float32Array(res);
}

function loadBinaryDODSFloat64(url)
// Read a Thredds dods binary of float64 file as an array of bytes.
// WARNING: Assumes little endian IEEE754
{
    responseText = readDODSHeader(url)

    res = []

    // This is like a "union", eightU8 and oneF64 are two different views of the same buffer.
    buf = new ArrayBuffer(8);
    eightU8 = new Uint8Array(buf)
    oneF64 = new Float64Array(buf)

    // Reads the rest of bytes as Float64
    for (var i = 0; i < responseText.length; i+=8)
    {
        eightU8[0] = responseText.charCodeAt(i+7) & 0xff
        eightU8[1] = responseText.charCodeAt(i+6) & 0xff
        eightU8[2] = responseText.charCodeAt(i+5) & 0xff
        eightU8[3] = responseText.charCodeAt(i+4) & 0xff
        eightU8[4] = responseText.charCodeAt(i+3) & 0xff
        eightU8[5] = responseText.charCodeAt(i+2) & 0xff
        eightU8[6] = responseText.charCodeAt(i+1) & 0xff
        eightU8[7] = responseText.charCodeAt(i  ) & 0xff
        res.push(oneF64*1.0)
    }

    return res;
}

function test1(map, lat, lon, inputData)
{
    var Nx = lon.length
    var Ny = lat.length

    var arr = []; // Initialize array
    var k = 0
    for (var j = 0 ; j < Ny; j++) {
        arr[j] = []; // Initialize inner array
        for (var i = 0; i < Nx; i++) {
            arr[j][i] = inputData[k]
            k++;
        }
    }


    var data = [{
      z: arr,
      x: lon,
      y: lat,
      zsmooth: 'best',
      type: 'heatmap',
      hoverongaps: false,
      connectgaps: false,
      showscale: false,
              colorscale:  [
    ['0.0', 'rgb(165,0,38)'],
    ['0.111111111111', 'rgb(215,48,39)'],
    ['0.222222222222', 'rgb(244,109,67)'],
    ['0.333333333333', 'rgb(253,174,97)'],
    ['0.444444444444', 'rgb(254,224,144)'],
    ['0.555555555556', 'rgb(224,243,248)'],
    ['0.666666666667', 'rgb(171,217,233)'],
    ['0.777777777778', 'rgb(116,173,209)'],
    ['0.888888888889', 'rgb(69,117,180)'],
    ['1.0', 'rgb(49,54,149)']
  ],

    }];

    console.log(map)

    var layout = {

        xaxis: {range: [Math.min(...lon), Math.max(...lon)], visible: false, fixedrange: true},
        yaxis: {range: [Math.min(...lat), Math.max(...lat)], visible: false, fixedrange: true},

        height: map._size.y,
        width:  map._size.x,
        margin: {pad: 0, border:0,l:0, r:0, t:0, b:0, autoexpand:true},
        paper_bgcolor: "#00000000",
        plot_bgcolor: "#00000000",



    };


    // Gives an id to the basemap, so Plotly can create the plot on top
    mapid = document.getElementById('mapid');
    mapid.childNodes[0].childNodes[0].id = 'baseMapId'  // Warning, assuming many things


    Plotly.newPlot('baseMapId', data, layout);

}


function getVelocityLayer(map)
// Creates and returns a velocity layer based on the datafiles.
{

    // Reads the files/urls
    lon  = loadBinaryDODSFloat64('./lon.bin')
    lat  = loadBinaryDODSFloat64('./lat.bin')
    data = loadBinaryDODSFloat32('./sample2.bin')

    // Creates the data structure.
    var Nx = lon.length
    var Ny = lat.length
    var layerData = [{header: {parameterUnit: "m.s-1", parameterNumber: 2,
                      parameterNumberName: "Eastward current", parameterCategory: 2,
                      lat: lat, lon: lon,
                      refTime: "2022-09-30 00:00:00"},
                      data: data.slice(0, Nx*Ny)},
                     {header: {parameterUnit: "m.s-1", parameterNumber: 3,
                      parameterNumberName: "Northward current", parameterCategory: 2,
                      lat: lat, lon: lon,
                      refTime: "2022-09-30 00:00:00"},
                      data: data.slice(-Nx*Ny)}]

    // Creates the leaflet velocity layer.
    var velocityLayer = L.velocityLayer({
        displayValues: true,
        displayOptions: {
          velocityType: "Global Wind",
          position: "bottomright",
          emptyString: "sss No wind data",

        },
        data: layerData,
        maxVelocity: 0.25,
        velocityScale: 0.3,
        lineWidth: 2,
        visible: true
      });

    test1(map, lat, lon, data.slice(0, Nx*Ny))


    return velocityLayer
}