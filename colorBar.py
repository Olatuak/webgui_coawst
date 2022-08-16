from browser import svg
# <linearGradient
#        id="linearGradient5682-1">
#       <stop
#          style="stop-color:#f0001a;stop-opacity:0.91489273;"
#          offset="0"
#          id="stop5678" />
#       <stop
#          style="stop-color:#ffffff;stop-opacity:0.95294118;"
#          offset="0.48991847"
#          id="stop5691" />
#       <stop
#          style="stop-color:#3370d7;stop-opacity:1;"
#          offset="1"
#          id="stop5680" />
#     </linearGradient>

def setupCMap(document, stops, colors):
    cmapGrad = document['cmapGrad']

    # Removes all initial stops in the gradient
    while cmapGrad.childElementCount>0:
        cmapGrad.removeChild(cmapGrad.children[0])

    # print(cmapGrad.__dict__)

    if len(stops) != len(colors):
        document <= 'Error, len(stops) != len(colors)'

    for i,stop in enumerate(stops):
        elemStop = document.createElementNS('http://www.w3.org/2000/svg','stop')
        elemStop.setAttribute('style', 'stop-color:%s' % colors[i])
        elemStop.setAttribute('offset', i/2.0)
        elemStop.setAttribute('id', 'cmapGradStopId%i' % i)
        cmapGrad.appendChild(elemStop)
        print(elemStop.__dict__)
                                                    # , {'style':'stop-color:#f0001a;stop-opacity:0.91489273;',
                                                    #         'offset': i/2.0, 'id' :"stop5678"}))




