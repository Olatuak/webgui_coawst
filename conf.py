from browser import window
import html as HTML
import datetime


JSDateOrig = datetime.datetime(1970,1,1,0,0,0,0,datetime.timezone.utc)

def convertDate(strDate):
    # WARNING: This function is fast, but not very flexible.
    # datetime.datetime.strptime(d.strip(), '%Y-%m-%dT%H:%M:%S.000Z')
    return datetime.datetime(int(strDate[:4]), int(strDate[5:7]), int(strDate[8:10]),
                             int(strDate[11:13]), int(strDate[14:16]), int(strDate[17:19]), 0, datetime.timezone.utc)

def convertPythonDateToJS(date):
    return (date - JSDateOrig).total_seconds()*1000

def convertJSDateToPython(JSDate):
    days = int(JSDate/86400000)
    milliseconds = (JSDate - days*86400000)
    return JSDateOrig + datetime.timedelta(days = days, milliseconds = milliseconds)


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



        # Reads the colorbars section
        try:
            colorbarSection = (treeConf.getElementsByTagName('colorbars'))[0]
            colorbars = colorbarSection.getElementsByTagName('colorbar')
            self.colorbars = {}
            for colorbar in colorbars:
                tempColorbar = {'name':        colorbar.getElementsByTagName('name'       )[0].innerHTML,
                                'longname':    colorbar.getElementsByTagName('longname'   )[0].innerHTML,
                                'abovemaxcol': colorbar.getElementsByTagName('abovemaxcol')[0].innerHTML,
                                'belowmincol': colorbar.getElementsByTagName('belowmincol')[0].innerHTML,
                                'units':       colorbar.getElementsByTagName('units'      )[0].innerHTML,
                                'style':       colorbar.getElementsByTagName('style'      )[0].innerHTML,
                                'min':         float(colorbar.getElementsByTagName('min')[0].innerHTML),
                                'max':         float(colorbar.getElementsByTagName('max')[0].innerHTML),
                               }
                name = colorbar.getElementsByTagName('name')[0].innerHTML
                self.colorbars[name] = tempColorbar


        except:
            print('ERROR: reading colorbars section of configuration file. Please check.')



        # Reads the basemaps section
        try:
            basemapsSection = (treeConf.getElementsByTagName('basemaps'))[0]
            basemaps = basemapsSection.getElementsByTagName('basemap')
            self.basemaps = []

            for basemap in basemaps:
                tempBasemap = {'name': basemap.getElementsByTagName('name')[0].innerHTML,
                               'url':  HTML.unescape(basemap.getElementsByTagName('url')[0].innerHTML),
                               'layer':HTML.unescape(basemap.getElementsByTagName('layer')[0].innerHTML),
                              }
                self.basemaps += [tempBasemap]

            self.basemap = self.basemaps[0]['url']

        except:
            print('ERROR: reading basemap section of configuration file. Please check.')



        # Reads the wms server section
        try:
            wmsServersSection = (treeConf.getElementsByTagName('wmsservers'))[0]
            wmsServers = wmsServersSection.getElementsByTagName('server')
            self.wmsServers = []

            for server in wmsServers:
                tempBasemap = {'name':            server.getElementsByTagName('name')[0].innerHTML,
                               'url':             HTML.unescape(server.getElementsByTagName('url'            )[0].innerHTML),
                               'featureinforeq':  HTML.unescape(server.getElementsByTagName('featureinforeq' )[0].innerHTML),
                               'capabilitiesreq': HTML.unescape(server.getElementsByTagName('capabilitiesreq')[0].innerHTML),
                               'type':            'wms',
                              }
                self.wmsServers += [tempBasemap]

            self.wmsURL = self.wmsServers[0]['url']

        except:
            print('ERROR: reading wms servers section of configuration file. Please check.')


        # Reads the opendap server section
        try:
            dapServersSection = (treeConf.getElementsByTagName('opendapservers'))[0]
            dapServers = dapServersSection.getElementsByTagName('server')
            self.dapServers = []

            for server in dapServers:
                timesVarName = server.getElementsByTagName('time')[0].innerHTML
                url = HTML.unescape(server.getElementsByTagName('url')[0].innerHTML)


                # Read the meshes.
                grids = {}
                for grid in server.getElementsByTagName('grid'):
                    gridName = grid.getAttribute('name')
                    floatType32 = (grid.getAttribute('floatType').lower() == 'float32')
                    if floatType32:
                        gridFloatBytes = 32
                    else:
                        gridFloatBytes = 64
                    gridLat, gridLon = grid.innerHTML.split(',')
#                     keyLon  = window.loadBinaryDODSFloat64ToCache(HTML.unescape(url.format(strTime = srtTime) + '?' + gridLat.strip() ))
#                     keyLat  = window.loadBinaryDODSFloat64ToCache(HTML.unescape(url.format(strTime = srtTime) + '?' + gridLon.strip() ))
                    grids[gridName] = [gridLat, gridLon, gridFloatBytes]

#                 # Parameters to convert the netCDF times into standard times.
#                 timeOffset        = float(server.getElementsByTagName('time')['0'].getAttribute('offset'))
#                 timeUnitsMillisec = float(server.getElementsByTagName('time')['0'].getAttribute('unitsToMilliseconds'))
                timeOffset = convertDate(server.getElementsByTagName('time')['0'].getAttribute('offset'))
                timeUnits = server.getElementsByTagName('time')['0'].getAttribute('units')
                if timeUnits == 'seconds':
                    timeUnitsInSeconds = 1
                elif timeUnits == 'minutes':
                    timeUnitsInSeconds = 60
                elif timeUnits == 'hours':
                    timeUnitsInSeconds = 3600
                elif timeUnits == 'days':
                    timeUnitsInSeconds = 86400
                timeFloatType = server.getElementsByTagName('time')['0'].getAttribute('floatType')
                if (timeFloatType.lower()=='float32'):
                    timeFloatBytes = 32
                else:
                    timeFloatBytes = 64




#
#                 # Converts the time into Date objects
#                 timeArray = []
#                 for i in range(dimsTime.sizes[0]):
#
#                     timeArray[i] = timeOffset + time[i]*timeUnitsInSeconds*1000

                tempBasemap = {'name':  server.getElementsByTagName('name')[0].innerHTML,
                               'url':   url,
                               'type':  'dap',
                               'grids': grids,
                               'time': timesVarName,
                               'timeOffset': timeOffset,
                               'timeUnitsInSeconds': timeUnitsInSeconds,
                               'timeFloatBytes': timeFloatBytes,
                              }
                self.dapServers += [tempBasemap]


        except:
            print('ERROR: reading opendap servers section of configuration file. Please check.')


        # Reads the layers section
        try:
            layersSection = (treeConf.getElementsByTagName('layers'))[0]
            layers = layersSection.getElementsByTagName('layer')

            self.layersVarNames = []
            self.layersVarShortNames = []
            self.layersVarLongNames = []  # All different variables that are represented as layers. This is used to structure
                                          # things in terms of variables, as for example, in menus.
            self.layers = []
            for layer in layers:
                tempLayer = {'name':        layer.getElementsByTagName('name'        )[0].innerHTML,
                             'server':      layer.getElementsByTagName('server'      )[0].innerHTML,
                             'servertype':  layer.getElementsByTagName('servertype'  )[0].innerHTML,
                             'layertype':   layer.getElementsByTagName('layertype'   )[0].innerHTML,
                             'gridtype':    layer.getElementsByTagName('gridtype'    )[0].innerHTML,
                             'varthreshold':layer.getElementsByTagName('varthreshold')[0].innerHTML,
                             'varscale':    layer.getElementsByTagName('varscale'    )[0].innerHTML,
                             'longname':    layer.getElementsByTagName('longname'    )[0].innerHTML,
                             'shortname':   layer.getElementsByTagName('shortname'   )[0].innerHTML,
                             'units':       layer.getElementsByTagName('units'       )[0].innerHTML,
                             'colorbar':    layer.getElementsByTagName('colorbar'    )[0].innerHTML,
                             'visible':     layer.getElementsByTagName('visible'     )[0].innerHTML.lower() == 'true',
                             'transparent': layer.getElementsByTagName('transparent' )[0].innerHTML.lower() == 'true',
                             }

                # Updates the server with the actual server dictionary of that name.
                servers = self.getServers(tempLayer['server'], tempLayer['servertype'])

#               # Is this a new type of variable we are representing?
                longName  = tempLayer['longname']
                shortName = tempLayer['shortname']
                name = tempLayer['name']
                if longName not in self.layersVarLongNames:
                    self.layersVarLongNames  += [longName .strip()]
                    self.layersVarShortNames += [shortName.strip()]
                    self.layersVarNames      += [name.strip()]

                # For each server it creates a new layer. This is an afterthought to simplify the configuration process,
                # originally each layer had on server.
                for server in servers:
                    tempLayer['server'] = server
                    print('PPPPP', server)
                    self.layers += [tempLayer.copy()]


        except:
            print('ERROR: reading layers section of configuration file. Please check.')


    def getLayer(self, server, varName):
        # Gets a layer based on the server it uses and the var name. If it doesn't find it, returns None.
        for layer in self.layers:
#             print('iiiiiii  ', layer['name'] , varName)
#             print(layer["server"]['name'] == server['name'])
#             print('ggg', layer["server"]['name'] , server['name'])
            if (layer['name'] == varName) and (layer["server"]['name'] == server['name']):
                print('iiiiiii  ', layer)
                return layer
        return None



    def getServers(self, names, serverType):
        # Gets a list of servers from a list of comma-separated server names
        servers = []
        while (names != ''):
            found = False
            idx = names.find(',')
            if (idx>-1):
                name = names[:idx].strip()
                names = names[idx+1:].strip()
            else:
                name = names.strip()
                names = ''

            if (serverType=='wms'):
                for server in self.wmsServers:
                    if (server['name'] == name):
                        servers += [server]
                        found = True
                        break
                if not found:
                    print('Error: server %s not found' % name)
                    return None

            elif (serverType=='dap'):
                for server in self.dapServers:
                    print('****',server['name'], name)
                    if (server['name'] == name):
                        servers += [server]
                        found = True
                        break
                if not found:
                    print('Error: server %s not found' % name)
                    return None


        return servers

