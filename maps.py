from browser import document, window
from colorBar   import *
# import velocityPythonAdaptor

reloadTileOnError = False

def onTileLoad(event):
    # print(event.__dict__)
    pass

def onTileLoadStart(event):
    pass


def onMapChange(event):
# Event called every time the map changes (pan, zoom)

    try:
        curLayer = event.sourceTarget
        window.updateHeatmap('baseMapId', curLayer)
    except:
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

        self.map = self.leaflet.map('mapid').setView(self.conf.viewcenter, self.conf.zoom)

        # Creates all the maps, plotlys and velocity layers.
        for layer in self.layers:
            colorBarName = layer['colorbar']
            colorbar = conf.colorbars[colorBarName]
            layerType  = layer['layertype']
            serverType = layer['servertype']
            print(1111)
            if layerType == 'colormap':
                if (serverType == 'wms'):
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

                    print(333, mapLayer)

                    mapLayer.on('tileload', onTileLoad)
                    mapLayer.on('tileerror', onError)
                    mapLayer.on('tileloadstart', onTileLoadStart)
                elif (serverType == 'dap'):
                    mapLayer = self.map
                else:
                    print('ERROR: invalid server type: ', serverType)

                self.listLayer +=[mapLayer]
                self.colorMaps += [newSVGCMapFromConfig(conf.colormaps[colorbar['style']])]
                self.colorBars += [createNewColorBar(self.colorMaps[-1], colorbar)]
            elif layerType == 'velocitymap':
                mapLayer = self.map
                velLayer = window.addNewVelocityLayer(mapLayer)
                velLayer.addTo(self.map)
                self.listLayer += [mapLayer]
                self.colorMaps += [None]
                self.colorBars += [None]

            else:
                pass


        self.update()



    def update(self):

        self.mainLayer = None
        # Sets the base map
        baseLayer = self.leaflet.tileLayer.wms(self.conf.basemaps[0]['url'], {'layers': self.conf.basemaps[0]['layer']})
        # self.map = self.leaflet.map('mapid').setView(self.conf.viewcenter, self.conf.zoom)
        self.map.options.crs = self.crs
        baseLayer.addTo(self.map)

        # self.map.on('zoomend', onMapChange)
        self.map.on('moveend', onMapChange)  # This event is called in zooms and pans


        self.updateLayers()

        self.map.setView(self.conf.viewcenter, self.conf.zoom)


    def updateLayers(self):
        resetColorBarsInMap(self.colorBars)  # Hide all color bars before visualizing only the ones that are visible.

        # Remove all previous layers.
        for mapLayer in self.listLayer:
            if self.map.hasLayer(mapLayer):
                self.map.removeLayer(mapLayer)
        try:
            window.clearHeatmap('baseMapId')
        except:
            pass

        try:
            window.clearVelocitymap('baseMapId')
        except:
            pass

        # Reversed because the first layer in the menu is the one on top
        for mapLayer, layer, colorBar in zip(reversed(self.listLayer), reversed(self.layers), reversed(self.colorBars)):

            if layer['visible']:
                print(555777, mapLayer, layer)

                layerType =  layer['layertype']
                serverType = layer['servertype']
                print(555777, mapLayer, layer)
                print('------')
                print('aaaaaaaaaaaaa', serverType, layerType)
                print('------')
                if layerType == 'colormap':
                    if serverType == 'wms':
                        mapLayer.addTo(self.map)

                    elif serverType == 'dap':
                        print('lllllllllll')
                        try:
                            window.addNewHeatMap(mapLayer)
                            window.updateHeatmap('baseMapId', mapLayer)
                        except:
                            pass

                    else:
                        print('ERROR, invalid server ', serverType)

                elif layerType == 'velocitymap':
                    if serverType == 'dap':
                        print('kkkkkkk')


                    else:
                        print('ERROR, invalid server ', serverType)




                if self.mainLayer is None:
                    self.mainLayer = mapLayer


                if colorBar is not None:
                    try:
                        addColorBarToMap(colorBar)
                    except:
                        pass






