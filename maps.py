from browser import document, window
from colorBar   import *
# import velocityPythonAdaptor

reloadTileOnError = False

def onTileLoad(event):
    # print(event.__dict__)
    pass

def onTileLoadStart(event):
    # print(343243243,event.__dict__)
    pass

def onMapZoom(event):
    # print(event.sourceTarget.__dict__)
    lat1 = 6.037500000000399
    lat2 = 45.7599999999984
    lon1 = -98
    lon2 = -55.63999999999942


    curLayer = event.sourceTarget
    # latlng1 = window.L.latLng(lat1, lon1)
    # p1 = event.sourceTarget.containerPointToLayerPoint(curLayer.latLngToContainerPoint(latlng1))
    # latlng2 = window.L.latLng(lat2, lon2)
    # p2 = event.sourceTarget.containerPointToLayerPoint(curLayer.latLngToContainerPoint(latlng2))

    # print(34333, window.L.point(0,0))
    q1 = event.sourceTarget.layerPointToLatLng(window.L.point(0,0))
    q2 = event.sourceTarget.layerPointToLatLng(window.L.point(1000, 800))
    bounds = curLayer.getBounds()

    pp = event.sourceTarget.containerPointToLayerPoint(window.L.point(0,0))
    # print(pp,pp.__dict__, q2,909, curLayer.getCenter().__dict__)
    update = {'xaxis': {'range': [bounds.getWest(),  bounds.getEast()],  'visible': False, 'fixedrange': True},
              'yaxis': {'range': [bounds.getSouth(), bounds.getNorth()], 'visible': False, 'fixedrange': True}}


    aa = document.getElementsByClassName('plot-container plotly')[0]
    aa.left = pp.x
    aa.top  = pp.y


    # update= {'width': p2.x - p1.x, 'height': p1.y - p2.y}

    window.Plotly.relayout('baseMapId', update)

    print(343243243)

    pass

def onError(event):
    # If there is an error loading a tile, recreates it.
    if reloadTileOnError:
        layer = event.target
        fragment = document.createDocumentFragment()
        layer._addTile(event.coords, fragment)
        layer._level.el.appendChild(fragment)


class Maps:

    def __init__(self, date, crs, conf, leaflet):

        self.crs = crs
        self.date = date
        self.layers = conf.layers
        self.conf = conf
        self.leaflet = leaflet

        self.listLayer = []
        self.colorMaps = []
        self.colorBars = []

        # Creates all the maps.
        for layer in self.layers:
            colorBarName = layer['colorbar']
            colorbar = conf.colorbars[colorBarName]
            mapLayer = self.leaflet.tileLayer.wms(layer['server']['url'], {
                'layers': layer['name'],
                'format': 'image/png',
                'transparent': True,
                'colorscalerange': '%.4f,%.4f' % (colorbar['min'], colorbar['max']),
                'abovemaxcolor': colorbar['abovemaxcol'],
                'belowmincolor': colorbar['belowmincol'],
                'time': self.date.strftime('%Y-%m-%dT%H:%M:00.0Z'),  # xxxxxxx
                'crs': self.crs,  # leaflet.CRS.EPSG3395,  # 'CRS:84'
                'version': '1.3.0',
                'styles': colorbar['style'],
            })

            mapLayer.on('tileload', onTileLoad)
            mapLayer.on('tileerror', onError)
            mapLayer.on('tileloadstart', onTileLoadStart)
            self.listLayer +=[mapLayer]
            self.colorMaps += [newCMapFromConfig(conf.colormaps[colorbar['style']])]
            self.colorBars += [createNewColorBar(self.colorMaps[-1], colorbar)]


        self.update()


    def update(self):

        self.mainLayer = None
        # Sets the base map
        baseLayer = self.leaflet.tileLayer.wms(self.conf.basemaps[0]['url'], {'layers': self.conf.basemaps[0]['layer']})
        self.map = self.leaflet.map('mapid').setView(self.conf.viewcenter, self.conf.zoom)
        self.map.options.crs = self.crs
        baseLayer.addTo(self.map)

        print(111)
        # self.map.on('zoomend', onMapZoom)
        self.map.on('moveend', onMapZoom)
        print(222)

        # window.test1()
        aaa = window.getVelocityLayer(self.map)

        # aaa.addTo(self.map)


        # bbbb = self.leaflet.map('mapid')
        # print(bbbb)
        # print(bbbb.__dict__)

        # aaa2 = window.getVelocityLayer()
        #
        # aaa2.addTo(self.map)




        # self.leaflet.VelocityLayer.addOverlay(aaa)
        # layerControl.addOverlay(aaa, "Ocean Current - Great Barrier Reef");
        # print(aaa.options.__dict__)
        # print(88888, self.leaflet.control.layers(self.map).__dict__)

        # self.leaflet.control.layers(self.map).addOverlay(aaa, 'fsdfdsfdsdfs')
        # print (document.__dict__)
        # class Uc:
        #     def __init__(self):
        #         self.header = {"parameterUnit": "m.s-1",
        #                     "parameterNumber": 2,
        #                     "dx": 1.0,
        #                     "dy": 1.0,
        #                     "parameterNumberName": "Eastward current",
        #                     "la1": -7.5,
        #                     "la2": -28.5,
        #                     "parameterCategory": 2,
        #                     "lo2": 156,
        #                     "nx": 3,
        #                     "ny": 3,
        #                     "refTime": "2017-02-01 23:00:00",
        #                     "lo1": 143},
        #         self.data = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9]
        #
        # class Vc:
        #     def __init__(self):
        #         self.header = {"parameterUnit": "m.s-1",
        #                     "parameterNumber": 2,
        #                     "dx": 1.0,
        #                     "dy": 1.0,
        #                     "parameterNumberName": "Eastward current",
        #                     "la1": -7.5,
        #                     "la2": -28.5,
        #                     "parameterCategory": 2,
        #                     "lo2": 156,
        #                     "nx": 3,
        #                     "ny": 3,
        #                     "refTime": "2017-02-01 23:00:00",
        #                     "lo1": 143},
        #         self.data = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9]
        #
        #
        # data = [ Uc(), Vc()     ]
        #
        # velocityLayer = self.leaflet.velocityLayer({
        #     'displayValues': True,
        #     'displayOptions': {
        #         'velocityType': "Global Wind",
        #         'position': "bottomleft",
        #         'emptyString': "No wind data"
        #     },
        #     'data': data,
        #     'maxVelocity': 15
        # })
        # velocityLayer.addTo(self.map)

        # self.updateLayers()

        self.map.setView(self.conf.viewcenter, self.conf.zoom)


    def updateLayers(self):

        resetColorBarsInMap(self.colorBars)  # Hide all color bars before visualizing only the ones that are visible.

        # Remove all previous layers.
        for mapLayer in self.listLayer:
            if self.map.hasLayer(mapLayer):
                self.map.removeLayer(mapLayer)

        # Reversed because the first layer in the menu is the one on top
        for mapLayer, layer, colorBar in zip(reversed(self.listLayer), reversed(self.layers), reversed(self.colorBars)):

            if layer['visible']:

                mapLayer.addTo(self.map)

                if self.mainLayer is None:
                    self.mainLayer = mapLayer



                addColorBarToMap(colorBar)






