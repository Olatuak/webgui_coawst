# This module controls the date gizmo.
from browser import alert, document, window, html, svg
import datetime

# Global variables
gizmoXPos = -1
isGizmoDown = False

x1RectDate = -1
x2RectDate = -1

onDateChange = None
layer = None


def onGizmoDateDown(event):
    global isGizmoDown, gizmoXPos

    gizmoXPos = event.x
    isGizmoDown = True

    # While the button is pressed, the whole document will be listening to events. This is so events work
    # outside the normally active elements.
    svgroot = document['root']
    svgroot.style['pointer-events'] = 'all'

def onGizmoDateUp(event):
    global isGizmoDown, gizmoXPos

    isGizmoDown = False
    gizmoXPos = -1

    # Makes the document unresponsive again (except for the normally avtive elements in the gizmo).
    # This allows leaflet to handle the rest of events.
    svgroot = document['root']
    svgroot.style['pointer-events'] = 'none'

    # Consolidates the transforms.
    transformList = document['gizmoDateHandle'].transform.baseVal
    transformList.consolidate()


def onGizmoDateMove(event):
    global isGizmoDown, gizmoXPos, pos, layer

    if isGizmoDown:

        dx = event.x - gizmoXPos
        gizmoXPos = event.x

        # Moves the handle with the mouse pointer.
        svgroot = document['root']
        translate = svgroot.createSVGTransform()
        mat = svgroot.getScreenCTM() # This is to convert screen coordinates into SVG units.
        translate.setTranslate(dx/mat.a, 0) # Hack: mat.a is the x scale of the document

        # Check that the date handle is between the limits
        rect = document['gizmoDateHandle'].getBoundingClientRect()
        xHandle = rect.left + rect.width/2.0
        dx = xHandle - x1RectDate
        if dx < 0:
            translate.setTranslate(-dx/mat.a, 0)
        dx = x2RectDate - xHandle
        if dx < 0:
            translate.setTranslate(dx/mat.a, 0)

        # Consolidates the transforms.
        transformList = document['gizmoDateHandle'].transform.baseVal
        transformList.appendItem(translate)
        transformList.consolidate()

        # Compute the location of the handle (as a value in [0,1]) and the date corresponding to this
        # location
        pos = (xHandle - x1RectDate)/(x2RectDate - x1RectDate)
        pos = max(min(pos, 1.0), 0.0)
        date = date1 + pos*(date2 - date1)
        gizmoDateText = document['gizmoDateText']
        gizmoDateText.text = '%.4i-%.2i-%.2i' % (date.year, date.month, date.day)

        if onDateChange is not None:
            onDateChange(layer, date)
        # print(gizmoDateText.text)



        # print(document['gizmoDateBubble'].getBoundingClientRect().__dict__)

def setupDateGizmo(lyr, dat1, dat2, onDateChng):
    global x1RectDate, x2RectDate
    global date1, date2
    global onDateChange
    global layer

    date1 = dat1
    date2 = dat2
    onDateChange = onDateChng
    layer = lyr

    document["gizmoDateHandle"].bind("mousedown", onGizmoDateDown)
    document["gizmoDateHandle"].bind("mouseup",   onGizmoDateUp)
    document["gizmoDateHandle"].bind("mousemove", onGizmoDateMove)
    document["root"           ].bind("mousemove", onGizmoDateMove)
    document["root"           ].bind("mouseup",   onGizmoDateUp)

    rect = document['rectDateGizmo'].getBoundingClientRect()
    x1RectDate = rect.left
    x2RectDate = rect.right
    print(x1RectDate,x2RectDate)
    # print (rect.__dict__)
