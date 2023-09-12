# This module controls the date gizmo.
from browser import alert, document, window, html, svg
import datetime
import javascript
# import math

# Global variables
isPlaying = False

xPointer = -1
xGizmo = 0.0
oldxPointerSVG = 0
isDateGizmoDown = False
selectedDateIdx = 0

x1RectDate = -1
x2RectDate = -1

onDateChange = None
layer = None
conf = None

dates = []
datePos = []
date1 = 0
date2 = 0

tickSVGelements = []

JSDateOrig = datetime.datetime(1970,1,1,0,0,0,0,datetime.timezone.utc)

def convertDate(strDate):
    # WARNING: This function is fast, but not very flexible.
    # datetime.datetime.strptime(d.strip(), '%Y-%m-%dT%H:%M:%S.000Z')
    return datetime.datetime(int(strDate[:4]), int(strDate[5:7]), int(strDate[8:10]),
                             int(strDate[11:13]), int(strDate[14:16]), int(strDate[17:19]), 0, datetime.timezone.utc)

def convertPythonDateToJS(date):
    global JSDateOrig
    return (date - JSDateOrig).total_seconds()*1000


def convertJSDateToPython(JSDate):
    days = int(JSDate/86400000)
    milliseconds = (JSDate - days*86400000.0)
    return JSDateOrig + datetime.timedelta(days = days, milliseconds = milliseconds)


def _binSearchDate(date, dates):
    # Performs a binary search for the closest date in 'dates' less than 'date'. WARNING: assumes 'dates' is ordered.

    iL = 0
    iR = len(dates) - 1
    iM = int(iR / 2)

    L = dates[iL]
    R = dates[iR]
    M = dates[iM]
    while (iR - iL > 1):
        if (date < M):
            R = M
            iR = iM
        else:
            L = M
            iL = iM

        iM = iL + int((iR - iL) / 2)
        M = dates[iM]

    return L, M, R, iL, iM, iR


def binSearchDateLess(date, dates):
    # Performs a binary search for the closest date in 'dates' less than 'date'. WARNING: assumes 'dates' is ordered.

    L, M, R, iL, iM, iR = _binSearchDate(date, dates)

    return iL


def binSearchDateLarger(date, dates):
    # Performs a binary search for the closest date in 'dates' larger than 'date'. WARNING: assumes 'dates' is ordered.

    L, M, R, iL, iM, iR = _binSearchDate(date, dates)

    return iR


def binSearchIdxDateCloser(date, dates):
    # Performs a binary search for the closest date in 'dates'. WARNING: assumes 'dates' is ordered.

    L, M, R, iL, iM, iR = _binSearchDate(date, dates)

    if date-L > R-date:
        return iR
    else:
        return iL


def onGizmoDateDown(event):
    global isDateGizmoDown, xPointer, oldxPointerSVG

    xPointer = event.x
    isDateGizmoDown = True

    svgroot = document['root']
    mat = svgroot.getScreenCTM()  # This is to convert screen coordinates into SVG units.
    oldxPointerSVG = (xPointer - mat.e) / mat.a

    # While the button is pressed, the whole document will be listening to events. This is so events work
    # outside the normally active elements.
    svgroot = document['root']
    svgroot.style['pointer-events'] = 'all'

def onGizmoPlay(event):
    global isPlaying
    isPlaying = not isPlaying
    print(777771, isPlaying)
    if isPlaying:
        document['iconPlay' ].style['fill-opacity'] = 0.0
        document['iconPause'].style['fill-opacity'] = 1.0
    else:
        document['iconPlay' ].style['fill-opacity'] = 1.0
        document['iconPause'].style['fill-opacity'] = 0.0
#     global selectedDateIdx
#     selectedDateIdx += 1
#     updateDateText()
#     updateGizmoPos(selectedDateIdx/(len(dates)-1))
#     if onDateChange is not None:
#         onDateChange(layer, selectedDateIdx)


def nextDate():
    global selectedDateIdx
    selectedDateIdx += 1
    if (selectedDateIdx>len(dates)):
        selectedDateIdx = 0
    updateDateText()
    updateGizmoPos(selectedDateIdx/(len(dates)-1))
    if onDateChange is not None:
        onDateChange(layer, selectedDateIdx)


def updateGizmoPos(pos):
    global oldxPointerSVG, xGizmo

    svgroot = document['root']
    mat = svgroot.getScreenCTM()  # This is to convert screen coordinates into SVG units.


    xnewGizmo = pos*(datePos[-1] - datePos[0])
#     xPointerSVG = (xGizmo - mat.e) / mat.a  # x position in SVG coordinates

    dx = (xnewGizmo - xGizmo) #/ mat.a

    xGizmo = xnewGizmo

    translate = svgroot.createSVGTransform()

    translate.setTranslate(dx, 0) # Hack: mat.a is the x scale of the document




    # Consolidates the transforms.
    transformList = document['gizmoDateHandle'].transform.baseVal
    transformList.appendItem(translate)
    transformList.consolidate()



def updateDateText():
    global isDateGizmoDown, xPointer, selectedDateIdx, dates


    selectDate = convertJSDateToPython(dates[selectedDateIdx])
    strDate = '%s' % selectDate.strftime('%Y-%m-%dT%H:%M')
    document['textDate2'].text = strDate
    document['gizmoDateText'].text = strDate


def onGizmoDateUp(event):
    global isDateGizmoDown, xPointer, selectedDateIdx, dates, layer

    if isDateGizmoDown:
        updateDateText()
        if onDateChange is not None:
            onDateChange(layer, selectedDateIdx)

        isDateGizmoDown = False
        xPointer = -1

        # Makes the document unresponsive again (except for the normally active elements in the gizmo).
        # This allows leaflet to handle the rest of events.
        svgroot = document['root']
        svgroot.style['pointer-events'] = 'none'

        # Consolidates the transforms. This is to avoid having a long list of transformations.
        transformList = document['gizmoDateHandle'].transform.baseVal
        transformList.consolidate()


def onGizmoDateMove(event):
    global isDateGizmoDown, xPointer, pos, layer, datePos, oldxPointerSVG, dates, xGizmo, selectedDateIdx, date1, date2
    
    
    if isDateGizmoDown:

        # dx = event.x - xPointer
        xPointer = event.x

        svgroot = document['root']
        mat = svgroot.getScreenCTM()  # This is to convert screen coordinates into SVG units.

        # # Moves the handle with the mouse pointer.
        # svgroot = document['root']
        # translate = svgroot.createSVGTransform()
        # mat = svgroot.getScreenCTM() # This is to convert screen coordinates into SVG units.
        # translate.setTranslate(dx/mat.a, 0) # Hack: mat.a is the x scale of the document

        xPointerSVG = (xPointer - mat.e) / mat.a  # x position in SVG coordinates

        # xPointerSVG = max(datePos[0],  xPointerSVG)
        # xPointerSVG = min(datePos[-1], xPointerSVG)

        dx = (xPointerSVG - oldxPointerSVG)
        xnewGizmo = xGizmo + dx
        xnewGizmo = max(xnewGizmo, 0)
        xnewGizmo = min(xnewGizmo, datePos[-1] - datePos[0])
        dx = xnewGizmo - xGizmo
        xGizmo = xnewGizmo

        # Moves the handle with the mouse pointer.
        translate = svgroot.createSVGTransform()

        translate.setTranslate(dx, 0) # Hack: mat.a is the x scale of the document

        # Compute the location of the handle (as a value in [0,1]) and the date corresponding to this
        # location

        pos = (xGizmo) / (datePos[-1] - datePos[0])


        # Consolidates the transforms.
        transformList = document['gizmoDateHandle'].transform.baseVal
        transformList.appendItem(translate)
        transformList.consolidate()

        # # Compute the location of the handle (as a value in [0,1]) and the date corresponding to this
        # # location
        # pos = (xHandle - x1RectDate)/(x2RectDate - x1RectDate)
        # pos = max(min(pos, 1.0), 0.0)
        date = date1 + pos*(date2 - date1)
        idxDate = binSearchIdxDateCloser(date, dates)  # Index of the existing date closer to the 'date'
        date = dates[idxDate]
        selectedDateIdx = idxDate
        # dateText = document['textDate']

        date = convertJSDateToPython(dates[idxDate])


        strDate = conf.datefmt % (date.year, date.month, date.day, date.hour, date.minute)
        gizmoDateText = document['gizmoDateText']
        gizmoDateText.text = strDate
#         # dateText.text = '%.4i-%.2i-%.2iT%.2i:%.2i' % (date.year, date.month, date.day, date.hour, date.minute)

        if onDateChange is not None:
            # onDateChange(layer, date)
            pass

        oldxPointerSVG = xPointerSVG





def setTicks(dates):
# Puts ticks along the dates line.

    global datePos, tickSVGelements


    datePos = []



    # First removes previous ticks (if exist)
    idx = 0
    while True:
        try:
            document['dateTick%i' % idx].remove()
        except:
            break

        idx += 1
    sampleTick = document['dateTick']

    # Computes the width of the dates line.
    widthDates = float(document['rectDateGizmo']['width']) - float(sampleTick['width'])
    # Creates all the ticks
    for idx, date in enumerate(dates):
        newTick = sampleTick.cloneNode(True)
        newTick['id'] = 'dateTick%i' % idx
        tickSVGelements += [newTick]
        xSample = float(sampleTick['x'])
        xTick = xSample + widthDates * idx / (len(dates) - 1)
        newTick['x'] = '%.4f' % xTick
        datePos += [xTick]
        sampleTick.parent.append(newTick)


def setupDateGizmo(lyr, dat1, dat2, JSdates, onDateChng, confFile):
    global x1RectDate, x2RectDate
    global date1, date2, dates, datePos, selectedDateIdx
    global onDateChange
    global layer
    global oldxPointerSVG, xGizmo
    global conf

    conf = confFile

    print(3456780)

    if dat1 is None:
        date1 = JSdates[0]
    else:
        date1 = convertPythonDateToJS(dat1)

    if dat2 is None:
        date2 = JSdates[-1]
    else:
        date2 = convertPythonDateToJS(dat2)



    oldxPointerSVG = -1
    xGizmo = 0.0
    selectedDateIdx = 0

    dates = []



    onDateChange = onDateChng
    layer = lyr

    # Computes the indices of the dates in 'dates' of the minimum set that contains dateStart-dateEnd
    idxDate1 = binSearchDateLess  (date1, JSdates)
    idxDate2 = binSearchDateLarger(date2, JSdates)

    idxDate1 = 0
    idxDate2 = len(JSdates)-1

    # Creates the set of datetime objects with the available dates
    for i in range(idxDate1, idxDate2+1):
        date = JSdates[i]
        dates += [date]

    setTicks(dates)

    # Starts the date labels with the first one
    date = convertJSDateToPython(dates[0])
    document['gizmoDateText'] =  conf.datefmt % (date.year, date.month, date.day, date.hour, date.minute)

    document["gizmoDateHandle"].bind("mousedown", onGizmoDateDown)
    document["gizmoDateHandle"].bind("mouseup",   onGizmoDateUp)
    document["gizmoDateHandle"].bind("mousemove", onGizmoDateMove)
    document["root"           ].bind("mousemove", onGizmoDateMove)
    document["root"           ].bind("mouseup",   onGizmoDateUp)
    document["play2"          ].bind("mousedown", onGizmoPlay)

    rect = document['rectDateGizmo'].getBoundingClientRect()
    x1RectDate = rect.left
    x2RectDate = rect.right

    updateDateText()

