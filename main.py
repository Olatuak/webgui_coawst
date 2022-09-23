from browser import alert, document, window, html, svg, ajax, aio
import datetime
import html as HTML

from dateGizmo  import *
from depthGizmo import *
from colorBar   import *


isPeeking = False
map = None

request = None

curDate = None

# layerName = 'significant_wave_height'
layerName = 'zeta'

dateStart = datetime.datetime(2019, 2, 16, 8, 0)
dateEnd   = datetime.datetime(2019, 2, 22, 8, 0)

dateStart = datetime.datetime(2022, 9, 22, 6, 30)
dateEnd   = datetime.datetime(2022, 9, 23, 0, 0)


world_map = document["mapid"]

# Access the leaflet.js API
leaflet = window.L

crs = leaflet.CRS.EPSG4326



def onDateChange(layer, date):
    global curDate

    curDate = date
    newDate = date.strftime('%Y-%m-%dT%H:%M:00.0Z')
    # newDate = date.strftime('%Y-%m-%dT')  #xxxxxx

    # print('>>>>>', newDate)
    layer.options  ['time'] = newDate
    layer.wmsParams['time'] = newDate
    # sapoWLLayer.setParams('time', '2020-09-23')
    # layer._map.invalidateSize()
    layer.redraw()
    # print(layer.__dict__.keys())


def onPointerMove(event):
    global isPeeking, map, layerName

    print (event.__dict__)

    latlngPointer = map.mouseEventToLatLng(event)

    # xy = map.mouseEventToLayerPoint(event)
    xy2 = map.mouseEventToContainerPoint(event)
    # oxy = map.getPixelOrigin()
    x = xy2.x
    y = xy2.y


    # xxyy = event.layerPoint()

    # print('{{}}', map.layerPointToContainerPoint(xy))

    if isPeeking:

        # print(666666 , map.getBounds().__dict__.keys())
        # print(5565656, map._layers[0].__dict__.keys())
        # print(545454, map._getMapPanePos())
        # print(4544543, map.getPixelOrigin())
        # print('}}}}}}',map.getPixelWorldBounds().getBottomLeft())
        # print('}}}}}}', map.getPixelWorldBounds().getTopRight ())
        mapSize = map.getSize()
        # print('$RRRRR ', map.__dict__.keys())

        strBBox = map.getBounds().toBBoxString()

        crs = 'CRS:84'

        fileFeatureInfo = open(reqFeatureInfo.format(wmsURL=wmsURL, layerName = layerName, crs=crs, strBBox=strBBox, mapSizeX=mapSize.x,
                                                     mapSizeY=mapSize.y, x=round(x), y=round(y), time=curDate.strftime('%Y-%m-%dT%H:%M:00.0Z')))
        txtFeatureInfo = fileFeatureInfo.read()

        parser = window.DOMParser.new()
        tree = parser.parseFromString(txtFeatureInfo, "application/xml")

        # elemDimension = tree.getElementsByTagName('longitude')
        # lon = elemDimension[0].innerHTML
        # elemDimension = tree.getElementsByTagName('latitude')
        # lat = elemDimension[0].innerHTML
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
    print('sssdsdsdssdfkdkdfkdf')

    # Allows for events and changes the cursor to cross hair
    document['root'].style.cursor = 'crosshair'
    document['root'].style.pointerEvents = 'all'
    # document['root'].style.cssText = 'pointer-events: all;'
    # document['mapid'].style.pointerEvents = 'none'


class Button(leaflet.Control):
    def onAdd(self, map):
        return html.BUTTON("hello") # ('<div id="header"> <H1>Your position</H1> </div>')


# data = {"maxZoom": 18,
#         "attribution": 'Map data &copy; ' \
#             '<a href="https://www.openstreetmap.org/">OpenStreetMap' \
#             '</a> contributors, <a href="https://creativecommons.org/' \
#             'licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
#             'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
#         "id": 'mapbox.streets'
#         }


fileConf = open('conf2.xml')
txtConf = fileConf.read()
parserConf = window.DOMParser.new()
treeConf = parserConf.parseFromString(txtConf, "application/xml")
wmsURL = (treeConf.getElementsByTagName('wmsurl'))[0].innerHTML
reqFeatureInfo  = HTML.unescape(treeConf.getElementsByTagName('featureinforeq' )[0].innerHTML)
reqCapabilities = HTML.unescape(treeConf.getElementsByTagName('capabilitiesreq')[0].innerHTML)


sapoWMS = wmsURL

sapoWLLayer = leaflet.tileLayer.wms(sapoWMS, {
    # 'layers':          'zeta',  #xxxxxxx
    'layers':          layerName,
    'format':          'image/png',
    'transparent':     True,
    'colorscalerange': '0,1.4',     #xxxxxxx
    # 'colorscalerange': '-0.4,0.4',
    'abovemaxcolor':   "extend",
    'belowmincolor':   "extend",
    'time':            dateStart.strftime('%Y-%m-%dT%H:%M:00.0Z'),   #xxxxxxx
    'crs': crs,  #leaflet.CRS.EPSG3395,  # 'CRS:84'
    'version': '1.3.0',
    # 'bounds': leaflet.latLngBounds([0.0,0.0],[10.0,10.0]),
    # 'center': '26.73, -81.975',
    # 'crs': leaflet.CRS.EPSG3857, #'CRS:84', #'EPSG:3857',
    # 'SRS': 'CRS:84', #'EPSG:3857',
    # 'time': '2022-08-10',
    # 'NUMCOLORBANDS':   250,
    # 'PALETTE':  ["#D73027", "#FC8D59", "#D9EF8B",],    #'scb_bugnylorrd',
    # 'styles': 'areafill/ferret',
    'styles': 'boxfill/ferret',
    # 'styles': 'areafill/scb_bugnylorrd',
    # 'sld_body': sldBody,
    # 'styles': 'raster-color-map',
})

cmap = setupCMapFerret(document, -0.0, 1.5)

print('MMMMMMMM', sapoWLLayer.__dict__.keys())
print('WMS', sapoWLLayer.wmsParams.__dict__.keys())
print('ffdfdfd', sapoWMS)

# def reqListener(a):
#     global request
#     print(1)
#     print('ggggg', request.__dict__)
#     print(2)
# str = reqCapabilities.format(wmsURL = sapoWMS, layerName = layerName, strTime = '2019-02-04T15:00:00.000Z')
#
# def on_complete(req):
#     print(' sdsdsds' , req.__dict__)
#
# req = ajax.ajax(headers={'crossDomain':'true','Access-Control-Allow-Origin':sapoWMS})
# req.bind('complete',on_complete)
#
# req.open('GET',str)
# # req.withCredentials=True
# print(123,req.getAllResponseHeaders())
#
# # req.set_header('crossDomain', 'true')
# # req.set_header('Access-Control-Allow-Origin', '*')
# req.send()
# print(1123,req.__dict__)
# # request = window.XMLHttpRequest.new()
# # request.open('GET', str)
# # request.setRequestHeader('Access-Control-Allow-Origin', 'https://icoast.rc.ufl.edu')
# # # # while True:
# # # print(request.__dict__)
# # request.responseType = 'arraybuffer'
# # request.onloadend = reqListener
# # print(111)
# # request.send()
# # print(222)
#
# # tryagain = True
# # while tryagain:
# #     print(456)
# #     try:
# #         print(request.__dict__)
# #         tryagain = False
# #     except:
# #         pass
# #     print(457)
# # date = open('https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd?request=GetCapabilities&service=WMS&version=1.3.0&layer=significant_wave_height&time=2019-02-04T15:00:00.000Z')
# stop
try:
    pass
    # fileCapabilities = open(reqCapabilities.format(wmsURL = sapoWMS, layerName = layerName, strTime = '2019-02-04T15:00:00.000Z'))
except:
    pass

print('ffdfdf111d', sapoWMS)
# sapoWMS

# a = ajax.open('GET', 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd?request=GetCapabilities&service=WMS&version=1.3.0&', False)

parser = window.DOMParser.new()


            # mode='text',
            # blocking=True)

# print(a.__dict__)
# print(a.read())
try:
    capabilities = fileCapabilities.read()

    # print('^^^^', capabilities)

    tree = parser.parseFromString(capabilities, "application/xml")
    capabilities = None
    # b = document(a)
    root = tree.firstChild.firstChild

    elemDimension = tree.getElementsByTagName('Dimension')
    # print(tree.textContent)
    txtDates = elemDimension[0].innerHTML.split(',')
except:
    txtDates = '2022-09-22T06:30:00.000Z,2022-09-22T07:00:00.000Z,2022-09-22T07:30:00.000Z,2022-09-22T08:00:00.000Z,2022-09-22T08:30:00.000Z,2022-09-22T09:00:00.000Z,2022-09-22T09:30:00.000Z,2022-09-22T10:00:00.000Z,2022-09-22T10:30:00.000Z,2022-09-22T11:00:00.000Z,2022-09-22T11:30:00.000Z,2022-09-22T12:00:00.000Z,2022-09-22T12:30:00.000Z,2022-09-22T13:00:00.000Z,2022-09-22T13:30:00.000Z,2022-09-22T14:00:00.000Z,2022-09-22T14:30:00.000Z,2022-09-22T15:00:00.000Z,2022-09-22T15:30:00.000Z,2022-09-22T16:00:00.000Z,2022-09-22T16:30:00.000Z,2022-09-22T17:00:00.000Z,2022-09-22T17:30:00.000Z,2022-09-22T18:00:00.000Z,2022-09-22T18:30:00.000Z,2022-09-22T19:00:00.000Z,2022-09-22T19:30:00.000Z'.split(',')



# print('MMMMMM', sapoWLLayer.wmsParams.__dict__)
# print('MMMMMM', sapoWLLayer.__dict__)
# getSource().updateParams({'TIME': startDate.toISOString()});
# updateInfo();
# star = svg.polygon(fill="red", stroke="blue", stroke_width="10",
#                    points=""" 0,0  75,38  90,80  135,80  98,107
#                              111,150 75,125  38,150 51,107
#                               15,80  60,80""")


# Create world map

# layer1 = leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
#     'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
#     'crossOrigin': 'anonymous'})
# layer1 = leaflet.tileLayer.wms('http://ows.mundialis.de/services/service?', {'layers': 'TOPO-OSM-WMS'})
layer1 = leaflet.tileLayer.wms('https://www.gebco.net/data_and_products/gebco_web_services/web_map_service/mapserv?', {'layers': 'gebco_latest'})
# layer1 = leaflet.tileLayer.wms('http://ows.mundialis.de/services/service?', {'layers': 'SRTM30-Colored-Hillshade'})
map = leaflet.map('mapid').setView([39.25, 2], 8)

# print('LLLL', document.__dict__.keys())

print(map.__dict__.keys())

map.options.crs = crs
# print('KKKKKK', map.options.crs.__dict__) #tobboxstring())
# a = leaflet.marker([39.2, 2.0]).addTo(map)


layer1.addTo(map)
sapoWLLayer.addTo(map)

map.setView([39.25, 2], 8)


# mymap.fitBounds([[20,-85],[35,-77]])

def onTileLoad(event):
    # if (not event.tile.complete):
    #     print(event.tile.__dict__.keys())
    #     event.tile._update()
    pass

def onError(event):
    # If there is an error loading a tile, recreates it.
    layer = event.target
    fragment = document.createDocumentFragment()
    layer._addTile(event.coords, fragment)
    layer._level.el.appendChild(fragment)

sapoWLLayer.on('tileload', onTileLoad)
sapoWLLayer.on('tileerror', onError)

# Put marker on map
# leaflet.marker([xyz.latitude, xyz.longitude]).addTo(map)

# helloPopup = leaflet.popup().setContent('Hello World!')

def testFunc(a, b):
    print('sdasdsas')
    d = leaflet.polygon([ [28.91,-77.07], [37.77, -69.43], [39.04, -85.2]], {'color': 'red'})
    d.addTo(map)
    btn = html.BUTTON("hello")
    map.getContainer() <= btn
    # print(repr(btn))
    # document.body.insertBefore(btn,
    #                            mymap.getContainer())
    # print('sd4334324s')

def testFunc2(a, b):
    global isPeeking, map

    isPeeking = True

    # Allows for events and changes the cursor to cross hair
    document['root'].style.cursor = 'crosshair'
    document['root'].style.pointerEvents = 'all'



    # print(sapoWLLayer.options['time'])
    # sapoWLLayer.options['time'] = '2020-09-23'
    # sapoWLLayer.wmsParams['time'] = '2020-09-23'
    # sapoWLLayer.setParams('time', '2020-09-23')
    # sapoWLLayer.redraw()
    # print(sapoWLLayer.options['time'])
    # mymap.invalidateSize()
    # print(sapoWLLayer.__dict__.keys())
    # print(' ---- ')
    # print(sapoWLLayer.wmsParams['time'])

    # leaflet.circle([50.5, 30.5], 200000, {'color': 'red'}).addTo(map)

# b1 = leaflet.easyButton('<span class="star">&starf;</span>', testFunc, 'text')
# b2 = leaflet.easyButton('<strong>A</strong>', testFunc2, 'text')
# b3 = leaflet.easyButton('&target;', testFunc, 'text')

# print(repr(b1.getContainer()))
capabilities = repr(map.getContainer())
# print(repr(a.attrs))

# mymap.addControl('<strong>A</strong>', 'topleft')

# leaflet.easyBar([b1, b2, b3]).addTo(map)


# button = Button(mymap)
# button.addTo(mymap)


# leaflet.easyButton('fa-globe', function(btn, map)
# {
#     helloPopup.setLatLng(map.getCenter()).openOn(map);
# }).addTo(YOUR_LEAFLET_MAP);

capabilities = leaflet.polygon(map, [leaflet.latLng(50.5, 30.5), leaflet.latLng(20.5, 20.5)])
map.addLayer(capabilities)

# setupDateGizmo(datetime.datetime(2022,1,1,0,0,0), datetime.datetime(2022,3,1,0,0,0))


curDate = dateStart

setupDateGizmo(sapoWLLayer, dateStart, dateEnd, txtDates, onDateChange)
setupDepthGizmo(0,10)

# cmap = setupCMap(document, [0,0.5,1], ['#f0ff1a', '#ffffff', '#3370d7'], -50, 50)

document["root"].bind("mousemove", onPointerMove)
document["root"].bind("mousedown", onPointerDown)

document["btnPoint"].bind("mouseup", onBtnPointClick)
document["btnPoint"].bind("onclick", onBtnPointClick)

# Hides the rectangle with the pointer values label
document['rectCoords'].attributeStyleMap.set('opacity', 0)
document['textCoords2'].text = ''

