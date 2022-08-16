from browser import alert, document, window, html, svg
import datetime
from dateGizmo  import *
from depthGizmo import *
from colorBar   import *



world_map = document["mapid"]

# Access the leaflet.js API
leaflet = window.L


def onDateChange(layer, date):
    newDate = date.strftime('%Y-%m-%dT%H:00:00.0Z')
    # newDate = date.strftime('%Y-%m-%dT')  #xxxxxx

    print('>>>>>', newDate)
    layer.options  ['time'] = newDate
    layer.wmsParams['time'] = newDate
    # sapoWLLayer.setParams('time', '2020-09-23')
    # layer._map.invalidateSize()
    layer.redraw()
    print(layer.__dict__.keys())

class Button(leaflet.Control):
    def onAdd(self, map):
        return html.BUTTON("hello") //('<div id="header"> <H1>Your position</H1> </div>')


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
    xyz = pos.coords
    lat = xyz.latitude
    lon = xyz.longitude

    # Display coordinates
    ul = html.UL(id="nav")
    ul <= html.LI(f'latitude: {xyz.latitude}')
    ul <= html.LI(f'longitude: {xyz.longitude}')
    document["coords"] <= ul

    sapoWMS = 'https://icoast.rc.ufl.edu/thredds/wms/coawst/snb/forecast/SNB_FORECAST_best.ncd'
    sapoWMS = 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd'  # xxxxxxxxx
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
        # 'time': '2022-08-10',
        # 'NUMCOLORBANDS':   250,
        # 'PALETTE':  ["#D73027", "#FC8D59", "#D9EF8B",],    #'scb_bugnylorrd',
        # 'styles': 'boxfill/occam',
        'styles': 'areafill/scb_bugnylorrd',
    })
    # getSource().updateParams({'TIME': startDate.toISOString()});
    # updateInfo();
    star = svg.polygon(fill="red", stroke="blue", stroke_width="10",
                       points=""" 0,0  75,38  90,80  135,80  98,107
                                 111,150 75,125  38,150 51,107
                                  15,80  60,80""")


    # Create world map
    mymap = leaflet.map('mapid').setView([51.505, -0.09], 2)
    layer1 = leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        'crossOrigin': 'anonymous'
    })

    layer1.addTo(mymap)
    sapoWLLayer.addTo(mymap)

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
    leaflet.marker([xyz.latitude, xyz.longitude]).addTo(mymap)

    helloPopup = leaflet.popup().setContent('Hello World!')

    def testFunc(a, b):
        print('sdasdsas')
        d = leaflet.polygon([ [28.91,-77.07], [37.77, -69.43], [39.04, -85.2]], {'color': 'red'})
        d.addTo(mymap)
        btn = html.BUTTON("hello")
        mymap.getContainer() <= btn
        # print(repr(btn))
        # document.body.insertBefore(btn,
        #                            mymap.getContainer())
        print('sd4334324s')

    def testFunc2(a, b):
        print('sdfsfdsffsfdsfdsdss')
        print(repr(star))

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

        leaflet.circle([50.5, 30.5], 200000, {'color': 'red'}).addTo(mymap)

    b1 = leaflet.easyButton('<span class="star">&starf;</span>', testFunc, 'text')
    b2 = leaflet.easyButton('<strong>A</strong>', testFunc2, 'text')
    b3 = leaflet.easyButton('&target;', testFunc, 'text')

    print(repr(b1.getContainer()))
    a = repr(mymap.getContainer())
    # print(repr(a.attrs))

    # mymap.addControl('<strong>A</strong>', 'topleft')

    leaflet.easyBar([b1, b2, b3]).addTo(mymap)


    # button = Button(mymap)
    # button.addTo(mymap)


    # leaflet.easyButton('fa-globe', function(btn, map)
    # {
    #     helloPopup.setLatLng(map.getCenter()).openOn(map);
    # }).addTo(YOUR_LEAFLET_MAP);

    d = leaflet.polygon(mymap, [leaflet.latLng(50.5, 30.5), leaflet.latLng(20.5, 20.5)])
    mymap.addLayer(d)

    # setupDateGizmo(datetime.datetime(2022,1,1,0,0,0), datetime.datetime(2022,3,1,0,0,0))
    setupDateGizmo(sapoWLLayer,
                   # datetime.datetime(2020, 9, 20, 0, 0, 0),
                   # datetime.datetime(2020, 9, 29, 0, 0, 0),
                   datetime.datetime(2022, 7, 29, 0, 0, 0),
                   datetime.datetime(2022, 8, 2, 0, 0, 0),
                   onDateChange)
    setupDepthGizmo(0,10)

    cmap = setupCMap(document, [0,0.5,1], ['#f0ff1a', '#ffffff', '#3370d7'])


def nonavi(error):
    document <= "Your browser doesn't support geolocation"

# Setup
geo = window.navigator.geolocation
if geo:
    geo.getCurrentPosition(navi, nonavi)
else:
    alert('geolocation not supported')