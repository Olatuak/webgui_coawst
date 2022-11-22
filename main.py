from browser import alert, document, window, html, svg, ajax, aio
import struct
import datetime
import html as HTML

from dateGizmo  import *
from depthGizmo import *
from colorBar   import *
from conf       import *
from layersMenu import *
from maps       import *


isPeeking = False

request = None

curDate = None



dateStart = datetime.datetime(2019, 2, 16, 8, 0)
dateEnd   = datetime.datetime(2019, 2, 22, 8, 0)

dateStart = datetime.datetime(2022, 9, 30, 0, 0)
dateEnd   = datetime.datetime(2022, 10, 6, 0, 0)


# Access the leaflet.js API
leaflet = window.L

crs = leaflet.CRS.EPSG4326




def onDateChange(layer, date):
    global curDate

    curDate = date
    newDate = date.strftime('%Y-%m-%dT%H:%M:00.0Z')
    # newDate = date.strftime('%Y-%m-%dT')  #xxxxxx

    layer.options  ['time'] = newDate
    layer.wmsParams['time'] = newDate
    # sapoWLLayer.setParams('time', '2020-09-23')
    # layer._map.invalidateSize()
    layer.redraw()


def onPointerMove(event):
    global isPeeking, layerName, mapLayers

    map = mapLayers.map
    latlngPointer = map.mouseEventToLatLng(event)

    xy2 = map.mouseEventToContainerPoint(event)
    x = xy2.x
    y = xy2.y

    if isPeeking:


        mapSize = map.getSize()

        strBBox = map.getBounds().toBBoxString()

        crs = 'CRS:84'


        server = conf.servers[0]

        print(999, server['featureinforeq'])
        print(9991, server['url'])
        layerName = 'zeta'
        featureReqUrl = server['featureinforeq'].format(wmsURL=server['url'], layerName = layerName, crs=crs, strBBox=strBBox, mapSizeX=mapSize.x,
                                                        mapSizeY=mapSize.y, x=round(x), y=round(y), time=curDate.strftime('%Y-%m-%dT%H:%M:00.0Z'))
        print(999333,featureReqUrl)
        fileFeatureInfo = open(featureReqUrl)
        txtFeatureInfo = fileFeatureInfo.read()

        parser = window.DOMParser.new()
        tree = parser.parseFromString(txtFeatureInfo, "application/xml")

        elemDimension = tree.getElementsByTagName('value')
        val = elemDimension[0].innerHTML

        document['textCoords2'].text = '%.3f, %.3f  =  %s' % (latlngPointer.lat, latlngPointer.lng, val)
        document['rectCoords'].attributeStyleMap.set('opacity', 1)


def onPointerDown(event):
    global isPeeking

    # Makes the SVG not to listen to mouse events (leaflet will still listening)
    if isPeeking:
        svgroot = document['root']
        svgroot.style['pointer-events'] = 'none'


    isPeeking = False

    # Hides the rectangle with the label
    document['rectCoords'].attributeStyleMap.set('opacity', 0)
    document['textCoords2'].text = ''


def onBtnPointClick(event):
    global isPeeking, map

    isPeeking = True

    # Allows for events and changes the cursor to cross hair
    document['root'].style.cursor = 'crosshair'
    document['root'].style.pointerEvents = 'all'



conf = Conf('confTDS.xml')



mapLayers = Maps(dateStart, crs, conf, leaflet)



# Creates the menu with the available layers
setupLayersMenu(conf, mapLayers)

#
# layerName = conf.layers[0]['name']
#
# sapoWMS = conf.wmsURL
#
# sapoWLLayer = leaflet.tileLayer.wms(sapoWMS, {
#     'layers':          layerName,
#     'format':          'image/png',
#     'transparent':     True,
#     'colorscalerange': '0,1.4',     #xxxxxxx
#     'abovemaxcolor':   "extend",
#     'belowmincolor':   "extend",
#     'time':            dateStart.strftime('%Y-%m-%dT%H:%M:00.0Z'),   #xxxxxxx
#     'crs': crs,  #leaflet.CRS.EPSG3395,  # 'CRS:84'
#     'version': '1.3.0',
#     # 'bounds': leaflet.latLngBounds([0.0,0.0],[10.0,10.0]),
#     # 'center': '26.73, -81.975',
#     # 'crs': leaflet.CRS.EPSG3857, #'CRS:84', #'EPSG:3857',
#     # 'SRS': 'CRS:84', #'EPSG:3857',
#     # 'time': '2022-08-10',
#     # 'NUMCOLORBANDS':   250,
#     # 'PALETTE':  ["#D73027", "#FC8D59", "#D9EF8B",],    #'scb_bugnylorrd',
#     # 'styles': 'areafill/ferret',
#     'styles': 'boxfill/ferret',
#     # 'styles': 'areafill/scb_bugnylorrd',
#     # 'sld_body': sldBody,
#     # 'styles': 'raster-color-map',
# })

# cmap = setupCMapFerret(document, -0.0, 1.5)

parser = window.DOMParser.new()

try:
    server = conf.servers[0]
    print('dddd',server['capabilitiesreq'].format(wmsURL = server['url'], layerName = conf.layers[0]['name'], strTime = '2019-02-04T15:00:00.000Z'))
    fileCapabilities = open(server['capabilitiesreq'].format(wmsURL = server['url'], layerName = conf.layers[0]['name'], strTime = '2019-02-04T15:00:00.000Z'))
    print('ffffff',fileCapabilities)
    capabilities = fileCapabilities.read()

    print('EYYYY', capabilities)


    tree = parser.parseFromString(capabilities, "application/xml")
    capabilities = None
    # b = document(a)
    root = tree.firstChild.firstChild

    elemDimension = tree.getElementsByTagName('Dimension')

    txtDates = elemDimension[0].innerHTML.split(',')
except:
    txtDates = '2022-09-22T00:00:00.000Z,2022-09-23T00:00:00.000Z,2022-09-24T00:00:00.000Z,2022-09-25T00:00:00.000Z,2022-09-26T00:00:00.000Z'.split(',')
    txtDates = '2022-09-30T00:00:00.000Z,2022-10-01T00:00:00.000Z,2022-10-02T00:00:00.000Z,2022-10-03T00:00:00.000Z,2022-10-04T00:00:00.000Z'.split(',')


print(1111111111, HTML.escape('https://icoast.rc.ufl.edu/thredds/dodsC/coawst/snb/forecast/runs/SNB_FORECAST_RUN_2022-10-27T06:00:00Z.ascii?ubar_eastward[0][0:1:2][0:1:2]'))
# fileFeatureInfo = open(r'https://icoast.rc.ufl.edu/thredds/dodsC/coawst/L0/forecast_qck/runs/NHCI_L0_QCK_RUN_2022-11-09T00:00:00Z.ascii?u_sur_eastward%5B0%5D%5B0:1:839%5D%5B0:1:1059%5D,v_sur_northward%5B0%5D%5B0:1:839%5D%5B0:1:1059%5D')
# fileFeatureInfo = open(r'https://icoast.rc.ufl.edu/thredds/dodsC/coawst/L0/forecast_qck/runs/NHCI_L0_QCK_RUN_2022-11-09T00:00:00Z.ascii?u_sur_eastward%5B0%5D%5B0:1:2%5D%5B0:1:2%5D,v_sur_northward%5B0%5D%5B0:1:2%5D%5B0:1:2%5D')
# fileFeatureInfo = open('sample.bin', 'rb')
# fileFeatureInfo = open('http://icoast.rc.ufl.edu/thredds/dodsC/coawst/L0/forecast_qck/runs/NHCI_L0_QCK_RUN_2022-11-09T00:00:00Z?u_sur_eastward[0][0:1:4][0:1:4],v_sur_northward[0][0:1:4][0:1:4]')
# # Avoids the header
# fileFeatureInfo.readline()
# fileFeatureInfo.readline()
# fileFeatureInfo.readline()
# fileFeatureInfo.readline()
# fileFeatureInfo.read(6)
# for i in range(900):
#     line = fileFeatureInfo.readline()
#     a = [float(x) for x in (line.split(',')[1:])]
#     print(i)



# Put marker on map
# leaflet.marker([xyz.latitude, xyz.longitude]).addTo(map)

curDate = dateStart

setupDateGizmo(mapLayers.mainLayer, dateStart, dateEnd, txtDates, onDateChange, conf)
setupDepthGizmo(0, 10, False)

# cmap = setupCMap(document, [0,0.5,1], ['#f0ff1a', '#ffffff', '#3370d7'], -50, 50)

document["root"].bind("mousemove", onPointerMove)
document["root"].bind("mousedown", onPointerDown)

document["btnPoint"].bind("mouseup", onBtnPointClick)
document["btnPoint"].bind("onclick", onBtnPointClick)

# Hides the rectangle with the pointer values label
document['rectCoords'].attributeStyleMap.set('opacity', 0)
document['textCoords2'].text = ''

