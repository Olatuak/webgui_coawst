from browser import window
import html as HTML

class Conf:
    def __init__(self, confFilename):

        print(confFilename)

        fileConf = open(confFilename)
        txtConf = fileConf.read()
        parserConf = window.DOMParser.new()
        treeConf = parserConf.parseFromString(txtConf, "application/xml")

        self.wmsURL = (treeConf.getElementsByTagName('wmsurl'))[0].innerHTML
        self.reqFeatureInfo = HTML.unescape(treeConf.getElementsByTagName('featureinforeq')[0].innerHTML)
        self.reqCapabilities = HTML.unescape(treeConf.getElementsByTagName('capabilitiesreq')[0].innerHTML)

        layersSection = (treeConf.getElementsByTagName('layers'))[0]
        layers = layersSection.getElementsByTagName('layer')

        self.layers = []

        for layer in layers:
            tempLayer = {'name':        layer.getElementsByTagName('name'       )[0].innerHTML,
                         'longname':    layer.getElementsByTagName('longname'   )[0].innerHTML,
                         'min':         layer.getElementsByTagName('min'        )[0].innerHTML,
                         'max':         layer.getElementsByTagName('max'        )[0].innerHTML,
                         'abovemaxcol': layer.getElementsByTagName('abovemaxcol')[0].innerHTML,
                         'belowmincol': layer.getElementsByTagName('belowmincol')[0].innerHTML,
                         'units':       layer.getElementsByTagName('units'      )[0].innerHTML,
                         'style':       layer.getElementsByTagName('style'      )[0].innerHTML}

            self.layers += [tempLayer]