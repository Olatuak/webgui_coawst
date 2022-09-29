from browser import document
from colorBar   import *

class Maps:

    def __init__(self, date, crs, conf, leaflet):

        self.crs = crs
        self.date = date
        self.layers = conf.layers
        self.conf = conf
        self.leaflet = leaflet

        self.update()


    def update(self):
        # Sets the base map
        baseLayer = self.leaflet.tileLayer.wms(self.conf.basemaps[0]['url'], {'layers': 'gebco_latest'})
        map = self.leaflet.map('mapid').setView([39.25, 2], 8)
        map.options.crs = self.crs
        baseLayer.addTo(map)

        # Adds all the visible maps.
        for layer in self.layers:

            mapLayer = self.leaflet.tileLayer.wms(layer['server']['url'], {
                'layers':          layer['name'],
                'format':          'image/png',
                'transparent':     True,
                'colorscalerange': '0,1.4',
                'abovemaxcolor':   "extend",
                'belowmincolor':   "extend",
                'time':            self.date.strftime('%Y-%m-%dT%H:%M:00.0Z'),   #xxxxxxx
                'crs': self.crs,  #leaflet.CRS.EPSG3395,  # 'CRS:84'
                'version': '1.3.0',
                'styles': layer['style'],
            })

            cmap = setupCMapFerret(document, -0.0, 1.5)

            mapLayer.addTo(map)

        map.setView([39.25, 2], 8)
