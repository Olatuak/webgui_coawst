from browser import alert, document, window, html, svg, ajax, aio


def onMenuClick(evt):
    print('aaaaaaaaaaaaaaaaaaaa', evt.toElement[ 'Idx'])

def setupLayersMenu(conf):

    # Populates the menu
    firstItemText          = document['txtLayer2']
    firstItemHighlightRect = document['rectHighlightItem1']

    # Creates at many svg menu entries as layers there are in the configuration file
    curItemText = firstItemText
    curItemText2 = curItemText.getElementsByTagName('tspan')[0]
    curItemHighlightRect = firstItemHighlightRect
    height = float(curItemHighlightRect['height'])
    listItemHighlightRect = []
    listItemText = []
    listItemText2 = []
    maxWidth = 0
    # yMenuText = curItemText.y
    # This loop makes the assumption that there is only at least one layer.
    for i, layer in enumerate(conf.layers):
        isLast = (i == len(conf.layers) - 1)

        # print('}}}}',curItemText.getElementsByTagName('tspan').__dict__)
        curItemText2.innerHTML = layer['longname']

        curItemHighlightRect['Idx'] = i
        curItemHighlightRect.bind("mousedown", onMenuClick)

        # Stores them in list for later use (fixing the x coordinate according to the final width)
        listItemHighlightRect += [curItemHighlightRect]
        listItemText          += [curItemText]
        listItemText2         += [curItemText2]


        if not isLast:
            parent = curItemText.parent

            # Finds the elements that conform each menu item (two for text, for svg reasons, one for the highlight rectangle).
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
