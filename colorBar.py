from browser import svg, document

idxCmap = 1
idxColorBar = 1
idxColorBarPos = 0

def resetColorBars(colorBars):
    global idxColorBarPos

    for colorBar in colorBars:
        colorBar.style['visibility'] = 'hidden'

    idxColorBarPos = 0


def showColorBar(colorBar):
    global idxColorBarPos

    colorBar.style['visibility'] = 'visible'
    colorBar['transform'] = 'translate(0,%.2f)' % (-idxColorBarPos * float(colorBar.getBBox().height) * 1.3)
    idxColorBarPos += 1


def createNewColorBar(cmap, layer):
    global idxColorBar

    # Clones the colorbar object, intially invisiblr
    templateColorBar = document["colorBar"]
    colorBar = templateColorBar.clone(True)
    colorBar['id'] = 'colorBar%i' % idxColorBar
    colorBar.style['visibility'] = 'hide'
    templateColorBar.parent.append(colorBar)

    # Set the new gradient.
    rectColorBar = colorBar.getElementsByTagName('rect')[0]
    style = rectColorBar['style']
    style.replace('cmapGrad', cmap)
    rectColorBar['style'] = style.replace('cmapGrad', cmap)

    colorBar.getElementsByClassName('txtUnits')[0].text = 'dasdas %s, %s' % (layer['longname'], layer['units'])
    colorBar.getElementsByClassName('textMinVal')[0].text = '%.2f' % layer['min']
    colorBar.getElementsByClassName('textMaxVal')[0].text = '%.2f' % layer['max']

    idxColorBar += 1

    return colorBar

def newCMap(stops, colors):
    global idxCmap

    cmapGrad = document['cmapGrad'].clone(True)
    cmapGrad['id'] = 'cmapGrad%i' % idxCmap
    document['cmapGrad'].parent.append(cmapGrad)
    idxCmap += 1

    # Removes all initial stops in the gradient
    while cmapGrad.childElementCount>0:
        cmapGrad.removeChild(cmapGrad.children[0])

    if len(stops) != len(colors):
        document <= 'Error, len(stops) != len(colors)'

    for i, stop in enumerate(stops):
        elemStop = document.createElementNS('http://www.w3.org/2000/svg','stop')
        elemStop.setAttribute('style', 'stop-color:%s' % colors[i])
        elemStop.setAttribute('offset', stop)
        elemStop.setAttribute('id', 'cmapGrad%iStopId%i' % (idxCmap, i))
        cmapGrad.appendChild(elemStop)

    return cmapGrad['id']

def newCMapFromConfig(confColormap):

    colors = confColormap['colors']
    stops  = confColormap['stops']

    strColors = []
    for i, color in enumerate(colors):
        strColors += ['#{:02X}{:02X}{:02X}'.format(round(color[0]*255), round(color[1]*255), round(color[2]*255))]

    return newCMap(stops, strColors)

def newCMapFerret(minVal, maxVal):

    colors = [[0.8,0.0,1.0],
              [0.3,0.2,1.0],
              [0.0,0.6,0.3],
              [1.0,1.0,0.0],
              [1.0,0.0,0.0],
              [0.6,0.0,0.0]]
    stops = [0.0/5, 1.0/5, 2.0/5, 3.0/5, 4.0/5, 5.0/5]

    strColors = []
    for i, color in enumerate(colors):
        strColors += ['#{:02X}{:02X}{:02X}'.format(round(color[0]*255), round(color[1]*255), round(color[2]*255))]

    return newCMap(stops, strColors, minVal, maxVal)
