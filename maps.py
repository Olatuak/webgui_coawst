from browser import document
from colorBar   import *

reloadTileOnError = True

def onTileLoad(event):
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
            mapLayer = self.leaflet.tileLayer.wms(layer['server']['url'], {
                'layers': layer['name'],
                'format': 'image/png',
                'transparent': True,
                'colorscalerange': '0,1.4',
                'abovemaxcolor': "extend",
                'belowmincolor': "extend",
                'time': self.date.strftime('%Y-%m-%dT%H:%M:00.0Z'),  # xxxxxxx
                'crs': self.crs,  # leaflet.CRS.EPSG3395,  # 'CRS:84'
                'version': '1.3.0',
                'styles': layer['style'],
            })

            mapLayer.on('tileload', onTileLoad)
            mapLayer.on('tileerror', onError)

            self.listLayer +=[mapLayer]
            print(8777, conf.colormaps.keys())
            self.colorMaps += [newCMapFromConfig(conf.colormaps[layer['style']])]
            self.colorBars += [createNewColorBar(self.colorMaps[-1], layer)]

        self.update()


    def update(self):

        self.mainLayer = None
        # Sets the base map
        baseLayer = self.leaflet.tileLayer.wms(self.conf.basemaps[0]['url'], {'layers': self.conf.basemaps[0]['layer']})
        self.map = self.leaflet.map('mapid').setView(self.conf.viewcenter, self.conf.zoom)
        self.map.options.crs = self.crs
        baseLayer.addTo(self.map)
        resetColorBars(self.colorBars) # Hide all color bars before visualizing only the ones that are visible.
        for mapLayer, layer, colorBar in zip(self.listLayer, self.layers, self.colorBars):

            if layer['visible']:

                mapLayer.addTo(self.map)

                if self.mainLayer is None:
                    self.mainLayer = mapLayer

                showColorBar(colorBar)

        self.map.setView(self.conf.viewcenter, self.conf.zoom)




