from browser import svg, document

idxCmap = 1
idxColorBar = 1
createdColorbars = []
addedColorbarNames = []
idxColorBarPos = 0

def resetColorBarsInMap(colorBars):
    # Hides all the colorbars in the map. There is a version of each different colorbar already in the string.
    global idxColorBarPos, addedColorbarNames, createdColorbars

    for colorBar in createdColorbars:
        colorBar.style['visibility'] = 'hidden'

    idxColorBarPos = 0
    addedColorbarNames = []



def addColorBarToMap(colorBar):
    # Shows and placesd in the right position the colorBar
    global idxColorBarPos, addedColorbarNames

    # Only one instance of each colorbar exists
    print(5555, colorBar['colorbarname'], addedColorbarNames)
    if colorBar['colorbarname'] in addedColorbarNames:
        return

    colorBar.style['visibility'] = 'visible'
    colorBar['transform'] = 'translate(0,%.2f)' % ( idxColorBarPos * float(colorBar.getBBox().height) * 1.3)

    idxColorBarPos += 1
    addedColorbarNames += [colorBar['colorbarname']]


def createNewColorBar(cmap, colorbar):
    global idxColorBar, createdColorbars

    # Only one instance of each colorbar is created
    for cbar in createdColorbars:

        if colorbar['name'] == cbar['colorbarname']:
            return cbar

    # Clones the colorbar object, intially invisiblr
    templateColorBar = document["colorBar"]
    svgColorBar = templateColorBar.clone(True)
    svgColorBar['id'] = 'colorBar%i' % idxColorBar
    svgColorBar.style['visibility'] = 'hide'
    svgColorBar['colorbarname'] = colorbar['name']
    templateColorBar.parent.append(svgColorBar)

    # Set the new gradient.
    rectColorBar = svgColorBar.getElementsByTagName('rect')[0]
    style = rectColorBar['style']
    style.replace('cmapGrad', cmap)
    rectColorBar['style'] = style.replace('cmapGrad', cmap)

    svgColorBar.getElementsByClassName('txtUnits')[0].text = '%s, %s' % (colorbar['longname'], colorbar['units'])
    svgColorBar.getElementsByClassName('textMinVal')[0].text = '%.2f' % colorbar['min']
    svgColorBar.getElementsByClassName('textMaxVal')[0].text = '%.2f' % colorbar['max']

    idxColorBar += 1
    createdColorbars += [svgColorBar]

    return svgColorBar

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
