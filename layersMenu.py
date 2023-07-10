from browser import alert, document, window, html, svg, ajax, aio

checkBoxes = '◇◈'

conf = None
mapLayers = None

listItemHighlightRect = []
listItemText = []
listItemText2 = []

listItemLayers = []
listItemLayersBox = []
itemsInColumn = []  # All the items that belong to a column.

def onMenuClick(evt):
    global conf

    idx = int(evt.toElement['Idx'])

    conf.layers[idx]['visible'] = not conf.layers[idx]['visible']

    updateLayersMenu()

    mapLayers.updateLayers()


def onMenuClick2(evt):
    # Called when any element in the menu table is clicked.
    global conf, itemsTextElement

    idx = int(evt.toElement['Idx'])
    layer = listItemLayers[idx]
    print(88899, idx, layer['name'])
    layer['visible'] = not layer['visible']

    updateLayersMenu2()

    mapLayers.updateLayers()


def onMenuClick3(evt):
    # Called when any column header in the menu table is clicked.
    global conf, itemsInColumn
    idx = int(evt.toElement['Idx'])
    itemsIdx = itemsInColumn[idx]
    print(itemsIdx, idx)
    print(listItemLayers[itemsIdx[0]])
    print(itemsIdx,'dfdfd')
    firstNonEmpty = 0
    while listItemLayers[itemsIdx[firstNonEmpty]] is None:
        firstNonEmpty += 1
        if firstNonEmpty >= len(itemsIdx):
            return
    selected = listItemLayers[itemsIdx[firstNonEmpty]]['visible']  #  Takes the value of the first one as a representative of the whole column
    for idx in itemsIdx:
        layer = listItemLayers[idx]
        if layer is not None:
            layer['visible'] = not selected


    updateLayersMenu2()

    mapLayers.updateLayers()


def updateLayersMenu():
    # Updates the text in the menus to reflect changes in the selected options
    for layer, curItemText2 in zip(conf.layers, listItemText2):
        visible = int((layer['visible']))
        curItemText2.innerHTML = checkBoxes[visible] + '  ' + layer['longname']


def updateLayersMenu2():
    # Updates the text in the menus to reflect changes in the selected options
    for layer, box in zip(listItemLayers, listItemLayersBox):
        if layer is not None:

            visible = int((layer['visible']))
#             print(box, 'pppp', box['style'])
            if visible==1:
                box['style'] = 'fill:#d45500;pointer-events: all;stroke:none;stroke-width:5.71539'
            else:
                box['style'] = 'fill:#e0e0e0;pointer-events: all;stroke:none;stroke-width:5.71539'

        else:
            box['style'] = 'fill:#a0a0a0;pointer-events: none;stroke:none;stroke-width:5.71539'


def setupLayersMenu(config, mapLyrs):

    global conf, mapLayers
    global listItemHighlightRect, listItemText, listItemText2

    conf = config
    mapLayers = mapLyrs

    # Populates the menu
    firstItemText          = document['txtLayer2']
    firstItemHighlightRect = document['rectHighlightItem1']

    # Creates at many svg menu entries as layers there are in the configuration file
    curItemText = firstItemText
    curItemText2 = curItemText.getElementsByTagName('tspan')[0]
    curItemHighlightRect = firstItemHighlightRect
    height = float(curItemHighlightRect['height'])

    maxWidth = 0
    # yMenuText = curItemText.y
    # This loop makes the assumption that there is at least one layer.
    for i, layer in enumerate(conf.layers):
        isLast = (i == len(conf.layers) - 1)

        visible = int((layer['visible']))
        curItemText2.innerHTML = checkBoxes[visible] + '  ' + layer['longname']

        curItemHighlightRect['Idx'] = i
        curItemHighlightRect.bind("mousedown", onMenuClick)

        # Stores them in list for later use (fixing the x coordinate according to the final width)
        listItemHighlightRect += [curItemHighlightRect]
        listItemText          += [curItemText]
        listItemText2         += [curItemText2]


        if not isLast:
            parent = curItemText.parent

            # Finds the elements that conform each menu item (two for text (for svg reasons), one for the highlight rectangle).
            curItemHighlightRect = curItemHighlightRect.cloneNode()
            curItemText          = curItemText.cloneNode(True)
            curItemText2         = curItemText.getElementsByTagName('tspan')[0]

            parent.append(curItemHighlightRect)
            parent.append(curItemText)

            # Locates them in the appropriate y coordinate
            curItemHighlightRect['y'] = '%.2f' % (float(curItemHighlightRect['y']) + height)
            curItemText['y'] = '%.2f' % (float(curItemText['y']) + height)
            curItemText2['y'] = '%.2f' % (float(curItemText2['y']) + height)

        # Computes the maximum width
        if curItemText2.getBBox().width > maxWidth:

            maxWidth = curItemText2.getBBox().width

    maxWidth *= 1.05

    # Adjust the x location and width of the rectangles
    for text, text2, highlight in zip(listItemText, listItemText2, listItemHighlightRect):
        oriWidth = float(highlight['width'])
        highlight['width'] = '%.3f' % maxWidth
        highlight['x'] = '%.3f' % (float(highlight['x']) + oriWidth - maxWidth)
        text     ['x'] = '%.3f' % (float(text     ['x']) + oriWidth - maxWidth)
        text2    ['x'] = '%.3f' % (float(text2    ['x']) + oriWidth - maxWidth)

        rectMenuLayer = document['rectLayer']
        rectMenuLayer['x'] = '%.3f' % (float(rectMenuLayer['x']) + oriWidth - maxWidth)
        rectMenuLayer['width'] = '%.3f' % (maxWidth*1.04)
        rectMenuLayer['height'] = '%.3f' % (((len(listItemText)+0.4) * height))


def setupLayersMenu2(config, mapLyrs):

    global conf, mapLayers
    global listItemHighlightRect, listItemText, listItemText2, listItemLayers, listItemLayersBox, itemsInColumn

    conf = config
    mapLayers = mapLyrs
    lastX = 0


    # Creates the table inside the menu.
    columnInfo = []
    rowInfo = []

    # computes the maximum width of the first column.
    maxColWidth = 1
    curItemText = document['txtMeshName']
    curItemText2 = curItemText.getElementsByTagName('tspan')[0]
    origColWidth = curItemText2.getBBox().width
    for i, dapServer in enumerate(conf.dapServers):
            serverName = dapServer['name']
            isLast = (i == len(conf.dapServers) - 1)

            curItemText2.innerHTML = serverName

            maxColWidth = max(maxColWidth, curItemText2.getBBox().width)
    xDisp = maxColWidth*.85 - origColWidth
    firstColPos = curItemText2.getBBox().x + xDisp

    # Creates as many columns as different variables are shown
    curItemText = document['txtVarName']
    curItemText2 = curItemText.getElementsByTagName('tspan')[0]
    curItemHighlightRect = document['rectVarName']
    height = float(curItemHighlightRect['height'])

    curItemHighlightRect['x'] = '%.4f' % (float(curItemHighlightRect['x']) + xDisp)
    curItemText ['x'] = '%.4f' % (float(curItemText ['x']) + xDisp)
    curItemText2['x'] = '%.4f' % (float(curItemText2['x']) + xDisp)


    for i, varName in enumerate(conf.layersVarShortNames):
        isLast = (i == len(conf.layersVarShortNames) - 1)

        curItemText2.innerHTML = varName

        curItemHighlightRect['Idx'] = i
        curItemHighlightRect.bind("mousedown", onMenuClick3)
        itemsInColumn += [[]]

        # Stores them in list for later use (fixing the x coordinate according to the final width)
        listItemHighlightRect += [curItemHighlightRect]
        listItemText          += [curItemText]
        listItemText2         += [curItemText2]

        width  = curItemText.getBBox().width*1.02
        height = curItemText.getBBox().height*1.02
        curItemHighlightRect['width'] = '%.4f' % (width)
        lastX = float(curItemHighlightRect['x']) + width
        columnInfo += [{'x': float(curItemHighlightRect['x']), 'y': float(curItemHighlightRect['y']),
                        'width': width, 'height': height, 'ctrl': curItemHighlightRect, 'varname': conf.layersVarNames[i]}]
        if not isLast:
            parent = curItemText.parent

            # Finds the elements that conform each menu item (two for text (for svg reasons), one for the highlight rectangle).
            curItemHighlightRect = curItemHighlightRect.cloneNode()
            curItemText          = curItemText.cloneNode(True)
            curItemText2         = curItemText.getElementsByTagName('tspan')[0]
            curItemHighlightRect['id'] = 'colItemHighlightRect%i' %i
            curItemText         ['id'] = 'colItemText%i' %i
            curItemText2        ['id'] = 'colItemText2%i' %i

            parent.append(curItemHighlightRect)
            parent.append(curItemText)



            # Locates them in the appropriate y coordinate
            curItemHighlightRect['x']     = '%.4f' % (float(curItemHighlightRect['x']) + width*1.02)

            curItemText ['x'] = '%.4f' % (float(curItemText ['x']) + width*1.02)
            curItemText2['x'] = '%.4f' % (float(curItemText2['x']) + width*1.02)


    # Creates as many svg menu rows as different servers are defined
    curItemText = document['txtMeshName']
    curItemText2 = curItemText.getElementsByTagName('tspan')[0]
    curItemHighlightRect = document['rectMeshName']
    height = float(curItemHighlightRect['height'])


    for i, dapServer in enumerate(conf.dapServers):
        serverName = dapServer['name']
        isLast = (i == len(conf.dapServers) - 1)

        curItemText2.innerHTML = serverName

        curItemHighlightRect['Idx'] = i
        curItemHighlightRect.bind("mousedown", onMenuClick)

        # Stores them in list for later use (fixing the x coordinate according to the final width)
        listItemHighlightRect += [curItemHighlightRect]
        listItemText          += [curItemText]
        listItemText2         += [curItemText2]

        height = curItemText.getBBox().height*1.05
        width  = curItemText.getBBox().width *1.05
        curItemHighlightRect['height'] = '%.4f' % (height)
        curItemHighlightRect['width' ] = '%.4f' % (maxColWidth+3)
        curItemText ['x'] = '%.4f' % (firstColPos)
        curItemText2['x'] = '%.4f' % (firstColPos)
        lastY = float(curItemHighlightRect['y']) + height
        rowInfo += [{'x': float(curItemHighlightRect['x']), 'y': float(curItemHighlightRect['y']),
                     'width': width, 'height': height, 'ctrl': curItemHighlightRect, 'server': dapServer}]
        if not isLast:
            parent = curItemText.parent

            # Finds the elements that conform each menu item (two for text (for svg reasons), one for the highlight rectangle).
            curItemHighlightRect = curItemHighlightRect.cloneNode()
            curItemText          = curItemText.cloneNode(True)
            curItemText2         = curItemText.getElementsByTagName('tspan')[0]
            curItemHighlightRect['id'] = 'rowItemHighlightRect%i' %i
            curItemText         ['id'] = 'rowItemText%i' %i
            curItemText2        ['id'] = 'rowItemText2%i' %i
            parent.append(curItemHighlightRect)
            parent.append(curItemText)



            # Locates them in the appropriate y coordinate
            curItemHighlightRect['y']     = '%.4f' % (float(curItemHighlightRect['y']) + height*1.05)

            curItemText ['y'] = '%.4f' % (float(curItemText ['y']) + height*1.05)
            curItemText2['y'] = '%.4f' % (float(curItemText2['y']) + height*1.05)




    # Creates all the options (layers that can be enabled or disabled)
    idx = 0
    rectMenuItemSample = document['rectMenuItemSample']
    for irow, row in enumerate(rowInfo):
        for icol, col in enumerate(columnInfo):
            idx += 1
            curItemHighlightRect = rectMenuItemSample.cloneNode()


            curItemHighlightRect['width']  = '%.4f' % (col['width'])
            curItemHighlightRect['height'] = '%.4f' % (row['height'])
            curItemHighlightRect['x'] = '%.4f' % (col['x'])
            curItemHighlightRect['y'] = '%.4f' % (row['y'])
            curItemHighlightRect['id'] = '%s_%i' % (rectMenuItemSample['id'], idx)

            try:
                layer = conf.getLayer(row['server'], col['varname'])
                listItemLayers += [layer]
                listItemLayersBox += [curItemHighlightRect]

                idx = len(listItemLayers) - 1
                curItemHighlightRect['Idx'] = idx
                itemsInColumn[icol] += [idx]
            except:
                curItemHighlightRect['Idx'] = None

            curItemHighlightRect.bind("mousedown", onMenuClick2)
            parent.append(curItemHighlightRect)

    rectMenuItemSample['visibility'] = 'hidden'




    # Resizes the menu and locates it right behind the button
    rectMenuLayers = document['rectMenuLayers']
    rectMenuLayers['width' ] = '%.4f' % (lastX - float(rectMenuLayers['x']) + 2)
    rectMenuLayers['height'] = '%.4f' % (lastY - float(rectMenuLayers['y']) + 2)
    btnLayer = document['btnLayer']
    btnX = float(btnLayer['x']) + float(btnLayer['width'])
    btnY = float(btnLayer['y']) + float(btnLayer['height'])
    menuX = float(rectMenuLayers['x']) + float(rectMenuLayers['width'])
    menuY = float(rectMenuLayers['y'])
    menuLayers = document['menuLayers2']
    for element in menuLayers.getElementsByTagName('*'):
        element['x'] = '%.4f' % (float(element['x']) + btnX - menuX)
        element['y'] = '%.4f' % (float(element['y']) + btnY - menuY - 1)


    updateLayersMenu2()









