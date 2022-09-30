from browser import window
import html as HTML

class Conf:
    def __init__(self, confFilename):

        fileConf = open(confFilename)
        txtConf = fileConf.read()
        parserConf = window.DOMParser.new()
        treeConf = parserConf.parseFromString(txtConf, "application/xml")

        strViewcenter = treeConf.getElementsByTagName('viewcenter')[0].innerHTML
        strViewcenter = strViewcenter.split([','])
        self.viewcenter = [float(strViewcenter[0]), float(strViewcenter[1])]
        self.zoom = int(treeConf.getElementsByTagName('viewzoom')[0].innerHTML)

        self.datefmt = treeConf.getElementsByTagName('datefmt')[0].innerHTML

        # Reads the colormaps section
        try:
            colormapsSection = (treeConf.getElementsByTagName('colormaps'))[0]
            colormaps = colormapsSection.getElementsByTagName('colormap')
            self.colormaps = {}

            for colormap in colormaps:
                tempColormap = {'name':   colormap.getElementsByTagName('name')[0].innerHTML,
                                'colors': eval(colormap.getElementsByTagName('colors')[0].innerHTML),
                                'stops':  eval(colormap.getElementsByTagName('stops')[0].innerHTML),
                               }
                name = colormap.getElementsByTagName('name')[0].innerHTML
                self.colormaps[name] = tempColormap


        except:
            print('ERROR: reading colormaps section of configuration file. Please check.')


        # Reads the basemaps section
        try:
            basemapsSection = (treeConf.getElementsByTagName('basemaps'))[0]
            basemaps = basemapsSection.getElementsByTagName('basemap')
            self.basemaps = []

            for basemap in basemaps:
                print(basemap)
                tempBasemap = {'name': basemap.getElementsByTagName('name')[0].innerHTML,
                               'url':  HTML.unescape(basemap.getElementsByTagName('url')[0].innerHTML),
                               'layer':HTML.unescape(basemap.getElementsByTagName('layer')[0].innerHTML),
                              }
                self.basemaps += [tempBasemap]

            self.basemap = self.basemaps[0]['url']

        except:
            print('ERROR: reading basemap section of configuration file. Please check.')

        # Reads the server section
        try:
            serversSection = (treeConf.getElementsByTagName('wmsservers'))[0]
            servers = serversSection.getElementsByTagName('server')
            self.servers = []

            for server in servers:
                tempBasemap = {'name':            server.getElementsByTagName('name'           )[0].innerHTML,
                              'url':             HTML.unescape(server.getElementsByTagName('url'            )[0].innerHTML),
                              'featureinforeq':  HTML.unescape(server.getElementsByTagName('featureinforeq' )[0].innerHTML),
                              'capabilitiesreq': HTML.unescape(server.getElementsByTagName('capabilitiesreq')[0].innerHTML),
                              }
                self.servers += [tempBasemap]

            self.wmsURL = self.servers[0]['url']

        except:
            print('ERROR: reading servers section of configuration file. Please check.')

        # Reads the layers section
        try:
            layersSection = (treeConf.getElementsByTagName('layers'))[0]
            layers = layersSection.getElementsByTagName('layer')
            self.layers = []
            for layer in layers:
                tempLayer = {'name':        layer.getElementsByTagName('name'       )[0].innerHTML,
                             'server':      layer.getElementsByTagName('server'     )[0].innerHTML,
                             'longname':    layer.getElementsByTagName('longname'   )[0].innerHTML,
                             'abovemaxcol': layer.getElementsByTagName('abovemaxcol')[0].innerHTML,
                             'belowmincol': layer.getElementsByTagName('belowmincol')[0].innerHTML,
                             'units':       layer.getElementsByTagName('units'      )[0].innerHTML,
                             'style':       layer.getElementsByTagName('style'      )[0].innerHTML,
                             'visible':     layer.getElementsByTagName('visible'    )[0].innerHTML.lower() == 'true',
                             'transparent': layer.getElementsByTagName('transparent')[0].innerHTML.lower() == 'true',
                             'min':         float(layer.getElementsByTagName('min')[0].innerHTML),
                             'max':         float(layer.getElementsByTagName('max')[0].innerHTML),

                             }

                # Updates the server with the actual server dictionary of that name.
                tempLayer['server'] = self.getServer(tempLayer['server'])

                self.layers += [tempLayer]
        except:
            print('ERROR: reading layers section of configuration file. Please check.')

    def getServer(self, name):
        for server in self.servers:
            if (server['name'] == name):
                return server

        print('Error: server %s not found' % name)
        return None