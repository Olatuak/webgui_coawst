from browser import document, window, timer
import dateGizmo
import colorBar
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


def nextFrame():
    if dateGizmo.isPlaying:
        dateGizmo.nextDate()

    timer.set_timeout(nextFrame, 200)


class Maps:

    def onDateChange(self, idxDate):

        try:
            date = self.dates[idxDate]
        except:
            return

        for mapLayer, layer, localDates in zip(reversed(self.listLayer), reversed(self.layers), reversed(self.localDates)):

            # Saves the date for later.
            try:
                layer['idxDate'] = localDates.index(date)
            except:
                layer['idxDate'] = 0


            if layer['visible']:

                layerType =  layer['layertype']
                serverType = layer['servertype']

                if serverType == 'dap':
                    try:
                        mapLayer.onDateChange(layer['idxDate'])
                    except:
                        pass

#         self.update()
        self.redrawLayers()


    def peekValues(self, lat, lon):

        # Clears the labels.
        for colorBar in self.colorBars:
            try:
                colorBar.getElementsByClassName('ColorbarValueText')[0].innerHTML = ''
            except:
                pass

        for mapLayer, layer, colorBar in zip(reversed(self.listLayer), reversed(self.layers), reversed(self.colorBars)):

            try:
                if layer['visible']:
                    layerType =  layer['layertype']
                    serverType = layer['servertype']
                    if serverType == 'dap':
                        value = mapLayer.peekValue(lat, lon)

                        colorBarValueText = colorBar.getElementsByClassName('ColorbarValueText')[0]
                        if len(value) == 1:
                            if value[0]<1e30 and not (value[0] != value[0]):    # Checks for nan
                                colorBarValueText.innerHTML = '%.2f' % value[0]

                        elif len(value) == 2:
                            if (value[0]<1e30) and (value[1]<1e30) and not (value[0] != value[0]):
                                colorBarValueText.innerHTML = '%.2f,%.2f' % (value[0], value[1])
            except:
                pass







    def __init__(self, date, crs, conf, leaflet):

        self.crs = crs
        self.date = date
        self.layers = conf.layers
        self.conf = conf
        self.leaflet = leaflet

        self.listLayer = []
        self.colorMaps = []
        self.colorBars = []
        self.localDates = [] # Each layer may have a different set of dates.

        self.map = self.leaflet.map('mapid').setView(self.conf.viewcenter, self.conf.zoom)

        # Creates all the maps and velocity layers.
        for layer in self.layers:
            def addLayer():
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

                        fileName = layer['server']['url']
                        JSDateOrig = datetime.datetime(1970,1,1,0,0,0,0,datetime.timezone.utc)
                        timeOffset = layer['server']['timeOffset']
                        fileName = fileName.format(year = 2023+0*date.year, month = 6+0*date.month, day = 22+0*date.day-1)
                        gridType = layer['gridtype'].split(',')
                        if len(gridType) == 1:
                            dynLayer, times = window.addNewDynHeatmapLayer(mapLayer, fileName,
                                                            layer['name'], layer['server']['grids'][gridType[0]],
                                                            layer['server']['time'],
                                                            (layer['server']['timeOffset'] - JSDateOrig).total_seconds(), int(layer['server']['timeUnitsInSeconds']),
                                                            int(layer['server']['timeFloatBytes']),
                                                            conf.colormaps[colorbar['style']], colorbar,  layer['varthresholdmin'], layer['varthresholdmax'], layer['visible'])
                        elif len(gridType) == 2:
                            dynLayer, times = window.addNewDynVectormapLayer(mapLayer, fileName,
                                                            layer['name'].split(','), layer['server']['grids'][gridType[0]], layer['server']['grids'][gridType[1]],
                                                            layer['server']['time'],
                                                            (layer['server']['timeOffset'] - JSDateOrig).total_seconds(), int(layer['server']['timeUnitsInSeconds']),
                                                            int(layer['server']['timeFloatBytes']),
                                                            conf.colormaps[colorbar['style']], colorbar, layer['varscale'], layer['varthresholdmax'], layer['visible'])
                        else:
                            print('ERROR, too many layers')
                        dynLayer.addTo(self.map)
                        layer['dynlayer'] = dynLayer
                        self.listLayer += [dynLayer]
                        self.colorMaps += [newSVGCMapFromConfig(conf.colormaps[colorbar['style']])]
                        self.colorBars += [createNewColorBar(self.colorMaps[-1], colorbar)]

                        # Finds the intersection of dates.
                        try:
                            if times is not None and times != []:
                                self.dates = list(set(self.dates).intersection(set(self.dates)))
                        except:
                            if times is not None and times != []:
                                self.dates= times
                        self.localDates += [times]
                    except:
                        self.listLayer += [None]
                        self.colorMaps += [None]
                        self.colorBars += [None]
                        self.localDates += [None]

                elif layerType == 'dynscatter':
                    try:
                        gridType     = layer['gridtype']
                        colorBarName = layer['colorbar']
                        colorbar = conf.colorbars[colorBarName]
                        mapLayer = self.map

                        fileName = layer['server']['url']
                        JSDateOrig = datetime.datetime(1970,1,1,0,0,0,0,datetime.timezone.utc)
                        timeOffset = layer['server']['timeOffset']
                        fileName = fileName.format(year = date.year, month = date.month, day = date.day)
                        gridType = layer['gridtype'].split(',')
                        dynScatterLayer = window.addNewDynScatterLayer(mapLayer, fileName,
                                                            layer['name'], layer['server']['grids'][gridType[0]],
                                                            conf.colormaps[colorbar['style']], colorbar,  layer['varthresholdmin'], layer['varthresholdmax'], layer['visible'])

                        dynScatterLayer.addTo(self.map)
                        layer['dynlayer'] = dynScatterLayer
                        self.listLayer += [dynScatterLayer]
                        self.colorMaps += [newSVGCMapFromConfig(conf.colormaps[colorbar['style']])]
                        self.colorBars += [createNewColorBar(self.colorMaps[-1], colorbar)]
                        self.localDates += [None]


                    except:
                        self.listLayer += [None]
                        self.colorMaps += [None]
                        self.colorBars += [None]
                        self.localDates += [None]
                else:
                    pass

            print(1111)
#             addLayer()
            try:
                def change_color():
#                     doc['first-text'].style.color = "blue"
                    print('4444')

                timer.set_timeout(addLayer,0)

#                 leaflet.
#                 dynLayer.draw()
#                 mapLayer.invalidateSize()

            except:
                pass
            print(1112)
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

                elif layerType == 'dynmap' or layerType == 'dynscatter':
                    if serverType == 'dap':
                        mapLayer.draw()

                    else:
                        print('ERROR, invalid server ', serverType)

        timer.set_timeout(nextFrame, 100)




    def updateLayers(self):
        resetColorBarsInMap(self.colorBars)  # Hide all color bars before visualizing only the ones that are visible.

#         print(4444, dateGizmo)
#         self.onDateChange(dateGizmo.selectedDateIdx)

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

            try:
                if layer['visible']:

                    try:
                        mapLayer.onDateChange(layer['idxDate'])
                    except:
                        pass
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

                    elif layerType == 'dynscatter':
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
            except:
                pass
        self.redrawLayers()









