from browser import alert, document, window, html, svg, ajax, timer
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


# dateStart = datetime.datetime(2019, 2, 16, 8, 0)
# dateEnd   = datetime.datetime(2019, 2, 22, 8, 0)

dateStart = datetime.datetime(2022, 1,  2, 0, 0, 0, 0, datetime.timezone.utc)
dateEnd   = datetime.datetime(2022, 10,  2, 0, 0, 0, 0, datetime.timezone.utc)
dateFile  = datetime.datetime(2022, 9, 28, 0, 0, 0, 0, datetime.timezone.utc)


# Access the leaflet.js API
leaflet = window.L

crs = leaflet.CRS.EPSG4326




def onDateChange(layer, date):
    global curDate

#     curDate = convertJSDateToPython(date)

    mapLayers.onDateChange(date)


def onPointerMove(event):
    global isPeeking, layerName, mapLayers

    map = mapLayers.map
    latlngPointer = map.mouseEventToLatLng(event)

    xy2 = map.mouseEventToContainerPoint(event)
    x = xy2.x
    y = xy2.y

    if isPeeking:
        values = mapLayers.peekValues(latlngPointer.lat, latlngPointer.lng)


#         mapSize = map.getSize()
#
#         strBBox = map.getBounds().toBBoxString()
#
#         crs = 'CRS:84'
#
#
#         server = conf.servers[0]
#
#         layerName = 'zeta'
#         featureReqUrl = server['featureinforeq'].format(wmsURL=server['url'], layerName = layerName, crs=crs, strBBox=strBBox, mapSizeX=mapSize.x,
#                                                         mapSizeY=mapSize.y, x=round(x), y=round(y), time=curDate.strftime('%Y-%m-%dT%H:%M:00.0Z'))
#         fileFeatureInfo = open(featureReqUrl)
#         txtFeatureInfo = fileFeatureInfo.read()
#
#         parser = window.DOMParser.new()
#         tree = parser.parseFromString(txtFeatureInfo, "application/xml")
#
#         elemDimension = tree.getElementsByTagName('value')
#         val = elemDimension[0].innerHTML

        try:
            document['textCoords2'].text = '%.3f, %.3f  =  %.3f' % (latlngPointer.lat, latlngPointer.lng, values[0])
        except:
            document['textCoords2'].text = '%.3f, %.3f' % (latlngPointer.lat, latlngPointer.lng)
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



# conf = Conf('confSNB.xml')
conf = Conf('confHurricanes.xml')


mapLayers = Maps(dateStart, crs, conf, leaflet)


# Creates the menu with the available layers
setupLayersMenu(conf, mapLayers)


parser = window.DOMParser.new()

try:
    server = conf.servers[0]
    fileCapabilities = open(server['capabilitiesreq'].format(wmsURL = server['url'], layerName = conf.layers[0]['name'], strTime = '2019-02-04T15:00:00.000Z'))
    capabilities = fileCapabilities.read()


    tree = parser.parseFromString(capabilities, "application/xml")
    capabilities = None
    # b = document(a)
    root = tree.firstChild.firstChild

    elemDimension = tree.getElementsByTagName('Dimension')

except:
    pass


# Put marker on map
# leaflet.marker([xyz.latitude, xyz.longitude]).addTo(map)

curDate = dateStart

setupDateGizmo(mapLayers.mainLayer, dateStart, dateEnd, mapLayers.dates, onDateChange, conf)
setupDepthGizmo(0, 10, False)

# cmap = setupCMap(document, [0,0.5,1], ['#f0ff1a', '#ffffff', '#3370d7'], -50, 50)

document["root"].bind("mousemove", onPointerMove)
document["root"].bind("mousedown", onPointerDown)

document["btnPoint"].bind("mouseup", onBtnPointClick)
document["btnPoint"].bind("onclick", onBtnPointClick)

# Hides the rectangle with the pointer values label
document['rectCoords'].attributeStyleMap.set('opacity', 0)
document['textCoords2'].text = ''

