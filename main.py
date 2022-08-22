from browser import alert, document, window, html, svg, ajax, aio
import datetime

from dateGizmo  import *
from depthGizmo import *
from colorBar   import *

isPeeking = False
map = None

world_map = document["mapid"]

# Access the leaflet.js API
leaflet = window.L

crs = leaflet.CRS.EPSG4326
# crs = leaflet.Proj.CRS.new('EPSG:3006',
# '+proj=utm +zone=33 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
# {
#     'resolutions': [
#         8192, 4096, 2048, 1024, 512, 256, 128,
#         64, 32, 16, 8, 4, 2, 1, 0.5
#     ],
#     'origin': [0, 0]
# })


def onDateChange(layer, date):
    newDate = date.strftime('%Y-%m-%dT%H:00:00.0Z')
    # newDate = date.strftime('%Y-%m-%dT')  #xxxxxx

    print('>>>>>', newDate)
    layer.options  ['time'] = newDate
    layer.wmsParams['time'] = newDate
    # sapoWLLayer.setParams('time', '2020-09-23')
    # layer._map.invalidateSize()
    layer.redraw()
    # print(layer.__dict__.keys())


def onPointerMove(event):
    global isPeeking, map

    # print (event.__dict__.keys())

    xy = map.mouseEventToLayerPoint(event)
    xy2 = map.mouseEventToContainerPoint(event)
    oxy = map.getPixelOrigin()
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
        B = map.containerPointToLatLng(xy)
        A = map.mouseEventToLatLng(event)
        c = map.unproject(xy2)

        # print(6666, A, b, c, strBBox)
        # print('7777   ', x, y, strBBox)
        print(x, y)
        a = open('https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd?service=WMS&version=1.3.0&request=GetFeatureInfo&CRS=%s&QUERY_LAYERS=significant_wave_height&BBOX=%s&INFO_FORMAT=text/xml&WIDTH=%i&HEIGHT=%i&I=%i&J=%i&FEATURE_COUNT=1&' % (crs, strBBox, mapSize.x, mapSize.y, x, y))
        print('https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd?service=WMS&version=1.3.0&request=GetFeatureInfo&CRS=%s&QUERY_LAYERS=significant_wave_height&BBOX=%s&INFO_FORMAT=text/xml&WIDTH=%i&HEIGHT=%i&I=%i&J=%i&FEATURE_COUNT=1&' % (crs, strBBox, mapSize.x, mapSize.y, x, y))
        b = a.read()
        # print('TRTRTR' , event.x, event.y, b)
        parser = window.DOMParser.new()
        tree = parser.parseFromString(b, "application/xml")
        root = tree.firstChild.firstChild
        elemDimension = tree.getElementsByTagName('longitude')
        lon = elemDimension[0].innerHTML
        elemDimension = tree.getElementsByTagName('latitude')
        lat = elemDimension[0].innerHTML
        elemDimension = tree.getElementsByTagName('value')
        val = elemDimension[0].innerHTML
        # print(A.__dict__)
        print(xy, xy2, oxy)
        print('}}}????  ', val, float(lon)-A.lng, float(lat)-A.lat)
        print('}}}????  ', float(lon)/ A.lng, float(lat)/ A.lat)
        print('2}}}????  ', float(lon) , A.lng, float(lat) , A.lat)



def onPointerDown(event):
    global isPeeking

    print('fjsdlfjdslfkjdslkfjdsl')

    isPeeking = False


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


def navi(pos):
    """Get position from window.navigator.geolocation and put marker on the
    map.
    """
    global map, crs

    xyz = pos.coords
    lat = xyz.latitude
    lon = xyz.longitude

    # Display coordinates
    ul = html.UL(id="nav")
    # ul <= html.LI(f'latitude: {xyz.latitude}')
    # ul <= html.LI(f'longitude: {xyz.longitude}')
    # document["coords"] <= ul

    sapoWMS = 'https://icoast.rc.ufl.edu/thredds/wms/coawst/snb/forecast/SNB_FORECAST_best.ncd'
    sapoWMS = 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd'  # xxxxxxxxx
    print(leaflet.Proj.CRS)

    # print(7654321, crs.__dict__.keys())
    sapoWLLayer = leaflet.tileLayer.wms(sapoWMS, {
        # 'layers':          'zeta',  #xxxxxxx
        'layers': 'significant_wave_height',
        'format':          'image/png',
        'transparent':     True,
        'colorscalerange': '0,1.4',     #xxxxxxx
        # 'colorscalerange': '-0.4,0.4',
        'abovemaxcolor':   "extend",
        'belowmincolor':   "extend",
        'time':            '2020-09-20',   #xxxxxxx
        'crs': crs,  #leaflet.CRS.EPSG3395,  # 'CRS:84'
        # 'bounds': leaflet.latLngBounds([0.0,0.0],[10.0,10.0]),
        # 'center': '26.73, -81.975',
        # 'crs': leaflet.CRS.EPSG3857, #'CRS:84', #'EPSG:3857',
        # 'SRS': 'CRS:84', #'EPSG:3857',
        # 'time': '2022-08-10',
        # 'NUMCOLORBANDS':   250,
        # 'PALETTE':  ["#D73027", "#FC8D59", "#D9EF8B",],    #'scb_bugnylorrd',
        # 'styles': 'boxfill/occam',
        'styles': 'areafill/scb_bugnylorrd',
        # 'styles': 'raster-color-map',
    })


    print('MMMMMMMM', sapoWLLayer.__dict__.keys())
    print('WMS', sapoWLLayer.wmsParams.__dict__.keys())
    date = open('https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd?request=GetCapabilities&service=WMS&version=1.3.0&layer=significant_wave_height&time=2019-02-04T15:00:00.000Z')

    # a = ajax.open('GET', 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd?request=GetCapabilities&service=WMS&version=1.3.0&', False)

    parser = window.DOMParser.new()


                # mode='text',
                # blocking=True)

    # print(a.__dict__)
    # print(a.read())
    date = date.read()

    # print(a)

    tree = parser.parseFromString(date, "application/xml")
    date = None
    # b = document(a)
    root = tree.firstChild.firstChild
    # print(root.localName)
    # print(root.tagName)
    # print(root.className)
    elemDimension = tree.getElementsByTagName('Dimension')
    # print(tree.textContent)
    txtDates = elemDimension[0].innerHTML.split(',')



    # print('MMMMMM', sapoWLLayer.wmsParams.__dict__)
    # print('MMMMMM', sapoWLLayer.__dict__)
    # getSource().updateParams({'TIME': startDate.toISOString()});
    # updateInfo();
    star = svg.polygon(fill="red", stroke="blue", stroke_width="10",
                       points=""" 0,0  75,38  90,80  135,80  98,107
                                 111,150 75,125  38,150 51,107
                                  15,80  60,80""")


    # Create world map

    # layer1 = leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    #     'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    #     'crossOrigin': 'anonymous'})
    # layer1 = leaflet.tileLayer.wms('http://ows.mundialis.de/services/service?', {'layers': 'TOPO-OSM-WMS'})
    layer1 = leaflet.tileLayer.wms('http://ows.mundialis.de/services/service?', {'layers': 'SRTM30-Colored-Hillshade'})
    map = leaflet.map('mapid').setView([39, 2], 8)

    a = leaflet.marker([39.2, 2.0]).addTo(map)

    print(map.__dict__.keys())

    map.options.crs = crs
    print('KKKKKK', map.options.crs.__dict__) #tobboxstring())



    layer1.addTo(map)
    sapoWLLayer.addTo(map)

    map.setView([39, 2], 8)

    print('KKKKKK', sapoWLLayer.options.__dict__)  # tobboxstring())
    print('KKKKK2', layer1.options.__dict__)  # tobboxstring())

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
    leaflet.marker([xyz.latitude, xyz.longitude]).addTo(map)

    helloPopup = leaflet.popup().setContent('Hello World!')

    def testFunc(a, b):
        print('sdasdsas')
        d = leaflet.polygon([ [28.91,-77.07], [37.77, -69.43], [39.04, -85.2]], {'color': 'red'})
        d.addTo(map)
        btn = html.BUTTON("hello")
        map.getContainer() <= btn
        # print(repr(btn))
        # document.body.insertBefore(btn,
        #                            mymap.getContainer())
        print('sd4334324s')


    def testFunc2(a, b):
        global isPeeking

        isPeeking = True

        document['root']['style'] = "pointer-events:all"
        # print(document['root'])
        # print(document['svg'].style)

        # document['svg'] <= star


        # print(sapoWLLayer.options['time'])
        # sapoWLLayer.options['time'] = '2020-09-23'
        # sapoWLLayer.wmsParams['time'] = '2020-09-23'
        # sapoWLLayer.setParams('time', '2020-09-23')
        sapoWLLayer.redraw()
        # print(sapoWLLayer.options['time'])
        # mymap.invalidateSize()
        # print(sapoWLLayer.__dict__.keys())
        # print(' ---- ')
        # print(sapoWLLayer.wmsParams['time'])

        leaflet.circle([50.5, 30.5], 200000, {'color': 'red'}).addTo(map)

    b1 = leaflet.easyButton('<span class="star">&starf;</span>', testFunc, 'text')
    b2 = leaflet.easyButton('<strong>A</strong>', testFunc2, 'text')
    b3 = leaflet.easyButton('&target;', testFunc, 'text')

    # print(repr(b1.getContainer()))
    date = repr(map.getContainer())
    # print(repr(a.attrs))

    # mymap.addControl('<strong>A</strong>', 'topleft')

    leaflet.easyBar([b1, b2, b3]).addTo(map)


    # button = Button(mymap)
    # button.addTo(mymap)


    # leaflet.easyButton('fa-globe', function(btn, map)
    # {
    #     helloPopup.setLatLng(map.getCenter()).openOn(map);
    # }).addTo(YOUR_LEAFLET_MAP);

    date = leaflet.polygon(map, [leaflet.latLng(50.5, 30.5), leaflet.latLng(20.5, 20.5)])
    map.addLayer(date)

    # setupDateGizmo(datetime.datetime(2022,1,1,0,0,0), datetime.datetime(2022,3,1,0,0,0))
    dateStart = datetime.datetime(2019, 2, 16, 8, 0)
    dateEnd   = datetime.datetime(2019, 2, 22, 8, 0)

    setupDateGizmo(sapoWLLayer, dateStart, dateEnd, txtDates, onDateChange)
    setupDepthGizmo(0,10)

    cmap = setupCMap(document, [0,0.5,1], ['#f0ff1a', '#ffffff', '#3370d7'])

    document["root"].bind("mousemove", onPointerMove)
    document["root"].bind("mousedown", onPointerDown)

def nonavi(error):
    document <= "Your browser doesn't support geolocation"

# Setup
geo = window.navigator.geolocation
if geo:
    geo.getCurrentPosition(navi, nonavi)
else:
    alert('geolocation not supported')