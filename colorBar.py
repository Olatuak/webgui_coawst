from browser import svg

def createNewColorBar():
    idColorBar = 1
    return idColorBar

def setupCMap(document, stops, colors, minVal, maxVal):
    cmapGrad = document['cmapGrad']

    # Removes all initial stops in the gradient
    while cmapGrad.childElementCount>0:
        cmapGrad.removeChild(cmapGrad.children[0])

    if len(stops) != len(colors):
        document <= 'Error, len(stops) != len(colors)'

    for i, stop in enumerate(stops):
        elemStop = document.createElementNS('http://www.w3.org/2000/svg','stop')
        elemStop.setAttribute('style', 'stop-color:%s' % colors[i])
        elemStop.setAttribute('offset', stop)
        elemStop.setAttribute('id', 'cmapGradStopId%i' % i)
        cmapGrad.appendChild(elemStop)

        document['textMinVal2'].text = '%.2f' % minVal
        document['textMaxVal2'].text = '%.2f' % maxVal
                                                    # , {'style':'stop-color:#f0001a;stop-opacity:0.91489273;',
                                                    #         'offset': i/2.0, 'id' :"stop5678"}))

def setupCMapFerret(document, minVal, maxVal):

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

    setupCMap(document, stops, strColors, minVal, maxVal)
