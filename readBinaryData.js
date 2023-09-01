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


function clearCache(url)
{
    for (c of cache)
    {
        c = null ;
    }
    cache.clear()

    totCache = 0;
    document.getElementById('txtCache').textContent = `${(totCache/1024/1024).toFixed(1)} mb`;
}

function readDODSHeader(url)
// Read the ASCII header of the otherwise binary dods file.
{
    let res = [];
    let str  = [];
    let req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.overrideMimeType('text\/plain; charset=x-user-defined');
    req.send(null);


    if (req.status == 404) console.log('ERROR reading ' + url);

    if (req.status > 299) return byteArray;


    // The binary data starts after some ascii data that ends in 'Data:'
    let foundData = false;
    for (let i = 0; i < req.responseText.length-5; ++i)
    {
        if (req.responseText.slice(i, i+5) == 'Data:')
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
    console.log('XXXXX ', url);
    let [dims, responseText] = readDODSHeader(url)


    // This is like a "union", fourU8 and oneF32 are two different views of the same buffer.
    buf = new ArrayBuffer(4);
    fourU8 = new Uint8Array(buf);
    oneF32 = new Float32Array(buf);

    bufArray = new ArrayBuffer(responseText.length+1);
    resArrayU8 = new Uint8Array(bufArray, 0, (responseText.length+1));
    resArrayF32 = new Float32Array(bufArray);

    // Reads the rest of bytes as Float32
    for (let i = 0; i < responseText.length; i+=4)
    {
        fourU8[0] = responseText.charCodeAt(i+3) & 0xff;
        fourU8[1] = responseText.charCodeAt(i+2) & 0xff;
        fourU8[2] = responseText.charCodeAt(i+1) & 0xff;
        fourU8[3] = responseText.charCodeAt(i  ) & 0xff;

        resArrayU8.set(fourU8, i);
    }

    return [dims, resArrayF32];
}

function loadBinaryDODSFloat64(url)
// Read a Thredds dods binary of float64 file as an array of bytes.
// WARNING: Assumes little endian IEEE754
{
    console.log('XXXXX ', url);
    let [dims, responseText] = readDODSHeader(url);

    // This is like a "union", eightU8 and oneF64 are two different views of the same buffer.
    let buf = new ArrayBuffer(8);
    let eightU8 = new Uint8Array(buf);
    let oneF64 = new Float64Array(buf);

    bufArray = new ArrayBuffer((responseText.length+1));
    resArrayU8 = new Uint8Array(bufArray, 0, (responseText.length+1));
    resArrayF64 = new Float64Array(bufArray);
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

        resArrayU8.set(eightU8, i);
    }

    return [dims, new Float32Array(resArrayF64)];
}

let loadTimeData = function loadTimeData(fileName, timeVar, timeFloatBytes) {

    let dimsTime, timesNC=0;
    // Read the time dimension
    if (timeFloatBytes==32) {
        [dimsTime, timesNC] = window.loadBinaryDODSFloat32Cached(fileName + '?' + timeVar);
    }
    else {
        [dimsTime, timesNC] = window.loadBinaryDODSFloat64Cached(fileName + '?' + timeVar);
    }
}
