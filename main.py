from browser import alert, document, window, html, svg, ajax, timer
import javascript
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

dateStart = datetime.datetime(2023, 1,  7, 0, 0, 0, 0, datetime.timezone.utc)
dateEnd   = datetime.datetime(2025, 10, 2, 0, 0, 0, 0, datetime.timezone.utc)

nowDate = javascript.Date.new(javascript.Date.now())
dateFile  = datetime.datetime(nowDate.getYear()+1900, nowDate.getMonth()+1, nowDate.getUTCDate(), 0, 0, 0, 0, datetime.timezone.utc)

document.getElementById('fileDate').valueAsDate = nowDate

# Access the leaflet.js API
leaflet = window.L

crs = leaflet.CRS.EPSG4326




def onDateChange(layer, date):
    # the date time changes (detetime *inside* a file, do not confuse with onFileDateChanged)
    global curDate

    mapLayers.onDateChange(date)


def onFileDateChange(event):
    # the date of the data file changes (do not confuse with onFileChange)
    print('XXXXXXXXX')
    dateFile = datetime.datetime.strptime(event.target.value, '%Y-%m-%d')
    print(dateFile)
    mapLayers.clearAll()

    mapLayers.__init__(dateFile, crs, conf, leaflet)

    pass



def onPointerMove(event):
    global isPeeking, layerName, mapLayers

    map = mapLayers.map
    latlngPointer = map.mouseEventToLatLng(event)

    xy2 = map.mouseEventToContainerPoint(event)
    x = xy2.x
    y = xy2.y

    if isPeeking:
        mapLayers.peekValues(latlngPointer.lat, latlngPointer.lng)

        document['textCoords2'].text = '%.3f, %.3f' % (latlngPointer.lat, latlngPointer.lng)
        document['rectCoords'].attributeStyleMap.set('opacity', 1)


def onPointerDown(event):
    global isPeeking

    # Makes the SVG not to listen to mouse events (leaflet will still listening)
    if isPeeking:
        svgroot = document['root']
        svgroot.style['pointer-events'] = 'none'


    isPeeking = False
    hideColorBarsValueBox(mapLayers.colorBars)

    # Hides the rectangle with the label
    document['rectCoords'].attributeStyleMap.set('opacity', 0)
    document['textCoords2'].text = ''


def onBtnPointClick(event):
    global isPeeking, map

    isPeeking = True
    showColorBarsValueBox(mapLayers.colorBars)

    # Allows for events and changes the cursor to cross hair
    document['root'].style.cursor = 'crosshair'
    document['root'].style.pointerEvents = 'all'



# conf = Conf('confSNB.xml')
conf = Conf('confHurricanes.xml')

mapLayers = Maps(dateFile, crs, conf, leaflet)


# Creates the menu with the available layers
# setupLayersMenu(conf, mapLayers)
setupLayersMenu2(conf, mapLayers)


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

document["root"].bind("mousemove", onPointerMove)
document["root"].bind("mousedown", onPointerDown)

document["btnPoint"].bind("mouseup", onBtnPointClick)
document["btnPoint"].bind("onclick", onBtnPointClick)

document["fileDate"].bind("change", onFileDateChange)



curDate = dateStart
setupDateGizmo(mapLayers.mainLayer, None, None, mapLayers.dates[:], onDateChange, conf)
setupDepthGizmo(0, 10, False)

# cmap = setupCMap(document, [0,0.5,1], ['#f0ff1a', '#ffffff', '#3370d7'], -50, 50)


# Hides the rectangle with the pointer values label
document['rectCoords'].attributeStyleMap.set('opacity', 0)
document['textCoords2'].text = ''

