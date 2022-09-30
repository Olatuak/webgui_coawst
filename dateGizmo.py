# This module controls the date gizmo.
from browser import alert, document, window, html, svg
import datetime
# import math

# Global variables
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


def convertDate(strDate):
    # WARNING: This function is fast, but not very flexible.
    # datetime.datetime.strptime(d.strip(), '%Y-%m-%dT%H:%M:%S.000Z')
    return datetime.datetime(int(strDate[:4]), int(strDate[5:7]), int(strDate[8:10]),
                             int(strDate[11:13]), int(strDate[14:16]), int(strDate[17:19]))

def binSearchDateLess(date, strDates):
    # Performs a binary search for the closest date in 'dates' less than 'date'. WARNING: assumes 'dates' is ordered.

    iL = 0
    iR = len(strDates) - 1
    iM = int(iR / 2)

    L = convertDate(strDates[iL].strip())
    R = convertDate(strDates[iR].strip())
    M = convertDate(strDates[iM].strip())
    while (iR - iL > 1):
        if (date < M):
            R = M
            iR = iM
        else:
            L = M
            iL = iM

        iM = iL + int((iR - iL) / 2)
        M = convertDate(strDates[iM].strip())

    return iM


def binSearchDateLarger(date, strDates):
    # Performs a binary search for the closest date in 'dates' larger than 'date'. WARNING: assumes 'dates' is ordered.

    iL = 0
    iR = len(strDates) - 1
    iM = int(iR / 2)

    L = convertDate(strDates[iL].strip())
    R = convertDate(strDates[iR].strip())
    M = convertDate(strDates[iM].strip())
    while (iR - iL > 1):
        if (date <= M):
            R = M
            iR = iM
        else:
            L = M
            iL = iM

        iM = iL + int((iR - iL) / 2)
        M = convertDate(strDates[iM].strip())

    return iM


def binSearchDateCloser(date, dates):
    # Performs a binary search for the closest date in 'dates'. WARNING: assumes 'dates' is ordered.

    iL = 0
    iR = len(dates) - 1
    iM = int(iR / 2)

    L = dates[iL]
    R = dates[iR]
    M = dates[iM]
    while (iR - iL > 1):
        if (date <= M):
            R = M
            iR = iM
        else:
            L = M
            iL = iM

        iM = iL + int((iR - iL) / 2)
        M = dates[iM]

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


def updateDateText():
    global isDateGizmoDown, xPointer, selectedDateIdx, dates

    selectDate = dates[selectedDateIdx]
    strDate = '%s' % selectDate.strftime('%Y-%m-%dT%H:%M')
    document['textDate2'].text = strDate
    document['gizmoDateText'].text = strDate


def onGizmoDateUp(event):
    global isDateGizmoDown, xPointer, selectedDateIdx, dates, layer

    if isDateGizmoDown:
        updateDateText()

        if onDateChange is not None:
            onDateChange(layer, dates[selectedDateIdx])

        isDateGizmoDown = False
        xPointer = -1

        # Makes the document unresponsive again (except for the normally avtive elements in the gizmo).
        # This allows leaflet to handle the rest of events.
        svgroot = document['root']
        svgroot.style['pointer-events'] = 'none'

        # Consolidates the transforms. This is to avoid having a long lst of transformations.
        transformList = document['gizmoDateHandle'].transform.baseVal
        transformList.consolidate()


def onGizmoDateMove(event):
    global isDateGizmoDown, xPointer, pos, layer, datePos, oldxPointerSVG, dates, xGizmo, selectedDateIdx
    
    
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

        xPointerSVG = (xPointer-mat.e) / mat.a  # x position in SVG coordinates
        # print('EEEEE ',xPointerSVG, mat.a, mat.b, mat.c, mat.d, mat.e, mat.f)

        # xPointerSVG = max(datePos[0],  xPointerSVG)
        # xPointerSVG = min(datePos[-1], xPointerSVG)

        # print('>><<>> ', xPointerSVG, oldxPointerSVG)
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
        print(date1, date2)
        date = date1 + pos*(date2 - date1)
        idxDate = binSearchDateCloser(date, dates)  # Index of the existing date closer to the 'date'
        date = dates[idxDate]
        selectedDateIdx = idxDate
        # dateText = document['textDate']

        idxDate = binSearchDateCloser(date, dates)
        date = dates[idxDate]

        strDate = conf.datefmt % (date.year, date.month, date.day, date.hour, date.minute)
        gizmoDateText = document['gizmoDateText']
        gizmoDateText.text = strDate
        # dateText.text = '%.4i-%.2i-%.2iT%.2i:%.2i' % (date.year, date.month, date.day, date.hour, date.minute)

        # print('JJJJJ', pos, dates[idxDate])

        if onDateChange is not None:
            # onDateChange(layer, date)
            pass

        oldxPointerSVG = xPointerSVG



        # print(document['gizmoDateBubble'].getBoundingClientRect().__dict__)


def setTicks(dates):
# Puts ticks along the dates line.

    print('>>>>>', dates)

    global datePos

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
        xSample = float(sampleTick['x'])
        xTick = xSample + widthDates * idx / (len(dates) - 1)
        newTick['x'] = '%.4f' % xTick
        datePos += [xTick]
        sampleTick.parent.append(newTick)


def setupDateGizmo(lyr, dat1, dat2, txtDates, onDateChng, confFile):
    global x1RectDate, x2RectDate
    global date1, date2, dates, datePos, selectedDateIdx
    global onDateChange
    global layer
    global oldxPointerSVG, xGizmo
    global conf

    conf = confFile

    oldxPointerSVG = -1
    xGizmo = 0.0
    selectedDateIdx = 0

    dates = []

    date1 = dat1
    date2 = dat2
    onDateChange = onDateChng
    layer = lyr

    # Computers the indices of the dates in 'dates' od the minimum set that contains dateStart-dateEnd
    idxDate1 = binSearchDateLess  (date1, txtDates)
    idxDate2 = binSearchDateLarger(date2, txtDates)

    # Creates the set of datetime objects with the available dates
    for i in range(idxDate1, idxDate2):
        txtDate = txtDates[i]
        txtDate = txtDate.strip()
        date = convertDate(txtDate)

        dates += [date]

    setTicks(dates)

    # Starts the date labels with the first one
    document['gizmoDateText'] =  conf.datefmt % (dates[0].year, dates[0].month, dates[0].day, dates[0].hour, dates[0].minute)

    document["gizmoDateHandle"].bind("mousedown", onGizmoDateDown)
    document["gizmoDateHandle"].bind("mouseup",   onGizmoDateUp)
    document["gizmoDateHandle"].bind("mousemove", onGizmoDateMove)
    document["root"           ].bind("mousemove", onGizmoDateMove)
    document["root"           ].bind("mouseup",   onGizmoDateUp)

    rect = document['rectDateGizmo'].getBoundingClientRect()
    x1RectDate = rect.left
    x2RectDate = rect.right

    updateDateText()

