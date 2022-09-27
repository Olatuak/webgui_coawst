from browser import alert, document, window, html, svg, ajax, aio


def setupLayersMenu(conf):

    # Hides the menu (it is visible so it can be edited)
    document['menuLayers']['opacity'] = '0'

    # Populates the menu
    firstItemText          = document['txtLayer1']
    firstItemHighlightRect = document['rectHighlightItem1']

    # Creates at many svg menu entries as layers there are in the configuration file
    curItemText = firstItemText
    curItemHighlightRect = firstItemHighlightRect
    # yMenuText = curItemText.y
    # This loop makes the assumption that there is only at least one layer.
    for i, layer in enumerate(conf.layers):
        isLast = (i == len(conf.layers) - 1)

        curItemText.innerHTML = layer['longname']

        if not isLast:
            parent = curItemText.parent
            height = float(curItemHighlightRect['height'])

            curItemHighlightRect = curItemHighlightRect.cloneNode()
            curItemText          = curItemText.cloneNode()

            curItemHighlightRect['y'] = '%.2f' % (float(curItemHighlightRect['y']) + height)
            curItemText['y']          = '%.2f' % (float(curItemText['y'])          + height)

            parent.append(curItemHighlightRect)
            parent.append(curItemText)

