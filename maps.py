from browser import document, window, timer
import dateGizmo
from colorBar   import *
import datetime
# import velocityPythonAdaptor

reloadTileOnError = False

def onTileLoad(event):
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

    def onDateChange(self, idxDate):

        for mapLayer, layer in zip(reversed(self.listLayer), reversed(self.layers)):

            if layer['visible']:

                layerType =  layer['layertype']
                serverType = layer['servertype']
                if serverType == 'dap':
                    mapLayer.onDateChange(idxDate)

#         self.update()
        self.redrawLayers()


    def peekValues(self, lat, lon):

        values = []
        for mapLayer, layer in zip(reversed(self.listLayer), reversed(self.layers)):

            if layer['visible']:

                layerType =  layer['layertype']
                serverType = layer['servertype']
                if serverType == 'dap':
                    values += [mapLayer.peekValue(lat, lon)]

        return values



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
                colorBarName = layer['colorbar']
                colorbar = conf.colorbars[colorBarName]
                mapLayer = self.map
                velLayer = window.addNewVelocityLayer(mapLayer)
                x = velLayer.addTo(self.map)
                self.listLayer += [x]
                self.colorMaps += [newSVGCMapFromConfig(conf.colormaps[colorbar['style']])]
                self.colorBars += [createNewColorBar(self.colorMaps[-1], colorbar)]
            elif layerType == 'dynmap':

                try:
                    gridType   = layer['gridtype']
                    colorBarName = layer['colorbar']
                    colorbar = conf.colorbars[colorBarName]
                    mapLayer = self.map

    #                 fileName = 'https://icoast.rc.ufl.edu/thredds/dodsC/matthew/L1_qck_20220928.nc.dods'
                    fileName = layer['server']['url']
                    JSDateOrig = datetime.datetime(1970,1,1,0,0,0,0,datetime.timezone.utc)
                    timeOffset = layer['server']['timeOffset']
                    fileName = fileName.format(year = date.year, month = date.month, day = date.day)
                    gridType = layer['gridtype'].split(',')
                    if len(gridType) == 1:

                        dynLayer, times = window.addNewDynHeatmapLayer(mapLayer, fileName,
                                                        layer['name'], layer['server']['grids'][gridType[0]],
                                                        layer['server']['time'],
                                                        (layer['server']['timeOffset'] - JSDateOrig).total_seconds(), int(layer['server']['timeUnitsInSeconds']),
                                                        int(layer['server']['timeFloatBytes']),
                                                        conf.colormaps[colorbar['style']], colorbar,  layer['varthreshold'])
                    elif len(gridType) == 2:
                        print(fileName)
                        dynLayer, times = window.addNewDynVectormapLayer(mapLayer, fileName,
                                                        layer['name'].split(','), layer['server']['grids'][gridType[0]], layer['server']['grids'][gridType[1]],
                                                        layer['server']['time'],
                                                        (layer['server']['timeOffset'] - JSDateOrig).total_seconds(), int(layer['server']['timeUnitsInSeconds']),
                                                        int(layer['server']['timeFloatBytes']),
                                                        conf.colormaps[colorbar['style']], colorbar, layer['varscale'], layer['varthreshold'])
                    else:
                        print('ERROR, too many layers')
                    dynLayer.addTo(self.map)
                    self.listLayer += [dynLayer]
                    self.colorMaps += [newSVGCMapFromConfig(conf.colormaps[colorbar['style']])]
                    self.colorBars += [createNewColorBar(self.colorMaps[-1], colorbar)]

                    self.dates = times
                except:
                    pass


            else:
                pass

        self.onDateChange(0)

#         self.update()





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



    def redrawLayers(self):

        try:
            self.mainLayer

        except:
            self.update()
            return


        # Reversed because the first layer in the menu is the one on top
        for mapLayer, layer, colorBar in zip(reversed(self.listLayer), reversed(self.layers), reversed(self.colorBars)):

            if layer['visible']:

                layerType =  layer['layertype']
                serverType = layer['servertype']
                if layerType == 'colormap':
#                     if serverType == 'wms':
#                         mapLayer.addTo(self.map)
#
#                     elif serverType == 'dap':
#                         # try:
#                         #     window.addNewHeatMap(mapLayer)
#                         #     window.updateHeatmap('baseMapId', mapLayer)
#                         # except:
#                         #     pass
#                         mapLayer.addTo(self.map)
#
#                     else:
#                         print('ERROR, invalid server ', serverType)
                    pass

#                 elif layerType == 'velocitymap':
#                     if serverType == 'dap':
#                         mapLayer.addTo(self.map)

                elif layerType == 'dynmap':
                    if serverType == 'dap':
                        mapLayer.draw()

                    else:
                        print('ERROR, invalid server ', serverType)

#         timer.set_timeout(self.redrawLayers, 10)




    def updateLayers(self):
        resetColorBarsInMap(self.colorBars)  # Hide all color bars before visualizing only the ones that are visible.

        # Remove all previous layers.
        for mapLayer in self.listLayer:
            if self.map.hasLayer(mapLayer):
                try:
                    self.map.removeLayer(mapLayer)
                except:
                    pass
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

                layerType =  layer['layertype']
                serverType = layer['servertype']
                if layerType == 'colormap':
                    if serverType == 'wms':
                        mapLayer.addTo(self.map)

                    elif serverType == 'dap':
                        # try:
                        #     window.addNewHeatMap(mapLayer)
                        #     window.updateHeatmap('baseMapId', mapLayer)
                        # except:
                        #     pass
                        mapLayer.addTo(self.map)

                    else:
                        print('ERROR, invalid server ', serverType)

                elif layerType == 'velocitymap':
                    if serverType == 'dap':
                        mapLayer.addTo(self.map)

                elif layerType == 'dynmap':
                    if serverType == 'dap':
                        mapLayer.addTo(self.map)

                    else:
                        print('ERROR, invalid server ', serverType)




                if self.mainLayer is None:
                    self.mainLayer = mapLayer


                if colorBar is not None:
                    try:
                        addColorBarToMap(colorBar)
                    except:
                        pass

        self.redrawLayers()









