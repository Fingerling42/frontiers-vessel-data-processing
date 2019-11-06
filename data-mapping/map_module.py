import folium
import json
import numpy
import branca
from branca.element import MacroElement
from jinja2 import Template

class bind_colormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(bind_colormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)  # noqa

def create_colormap(segment, caption):
    indexes = []
    palette = []
    for i in range(0,len(segment)):
        indexes.append(segment[i]['rang'][0])
        palette.append(segment[i]['color'])
    indexes.append(segment[len(segment)-1]['rang'][1])

    maxIndex = max(indexes)
    minIndex = min(indexes)
    
    colormap = branca.colormap.LinearColormap(palette, vmin=minIndex, vmax=maxIndex)
    colormap = colormap.to_step(index=indexes)
    colormap.caption = caption
    return colormap

def draw_points_group(points, sample, groupName, show):

    ## Design for points
    radius = 15
    segment = [ {'color': '#8800f8'},   # purple
                {'color': '#0010ff'},   # blue
                {'color': '#007fff'},   # azure
                {'color': '#00f8ff'},   # cyan
                {'color': '#00ff99'},   # spring
                {'color': '#00ff07'},   # green
                {'color': '#78ff00'},   # lime
                {'color': '#fff800'},   # yellow
                {'color': '#ff8000'},   # orange
                {'color': '#ff0a00'}    # red
    ]

    ## Create a group
    fgv = folium.FeatureGroup(name=groupName, show=show)

    ## Find min and max value and step
    paramMin = min([x[sample] for x in points])
    paramMax = max([x[sample] for x in points])
    segmentStep = (paramMax - paramMin) / len(segment)

    ## For each segment find color
    segment[0].update({'rang': (paramMin, paramMin + segmentStep)})

    for i in range(1,len(segment)-1):
        param = segment[i-1]['rang'][1]
        segment[i].update({'rang': (param, param + segmentStep)})

    param = segment[i]['rang'][1]
    segment[len(segment)-1].update({'rang': (param, paramMax)})

    for i in range(0,len(segment)):
        segment[i].update({'sumPoints': 0})

    ## Draw a point depending on the hit in the segment
    for point in points:

        for i in range(0,len(segment)):
            if point.get(sample) >= segment[i]['rang'][0] and point.get(sample) <= segment[i]['rang'][1]:
                pointColor = segment[i].get('color')
                segment[i]['sumPoints'] += 1
                break

        folium.CircleMarker(location=(point.get('coord')),
            radius=radius,
            color=pointColor,
            popup='Coord: {coord}\n{sample}: {cond}'.format(coord=point.get('coord'), sample=sample, cond=point.get(sample)),
            stroke=True,
            weight=1,
            fill=True).add_to(fgv)

    return fgv, segment

def get_data_points():
## Get data from files

    points = []
    numPoints = 0

    ## Prepare files

    timeFile = open('../times.txt', 'r')
    tempFile = open('../temperature.txt', 'r')
    phFile = open('../phs.txt', 'r')
    oxyPercentFile = open('../oxygen_percent.txt', 'r')
    oxyMglFile = open('../oxygen_mgl.txt', 'r')
    condFile = open('../conductivity.txt', 'r')
    coordFile = open('../coordinates_real.txt', 'r')

    ## Extract time
    for line in timeFile:
        points.append(dict(time=float(line[0:line.find('\n')])))

    ## Extract temperature
    for line in tempFile:
        points[numPoints].update({'tempr': float(line[0:line.find('\n')])})
        numPoints += 1

    numPoints = 0

    ## Extract pH
    for line in phFile:
        points[numPoints].update({'ph': float(line[0:line.find('\n')])})
        numPoints += 1

    numPoints = 0

    ## Extract oxygen in percentage
    for line in oxyPercentFile:
        points[numPoints].update({'oxy_percent': float(line[0:line.find('\n')])})
        numPoints += 1

    numPoints = 0

    ## Extract oxygen in mg / l
    for line in oxyMglFile:
        points[numPoints].update({'oxy_mgl': float(line[0:line.find('\n')])})
        numPoints += 1

    numPoints = 0

    ## Extract electrical conductivity
    for line in condFile:
        points[numPoints].update({'cond': float(line[0:line.find('\n')])})
        numPoints += 1

    numPoints = 0

    ## Extract geo coords
    for line in coordFile:
        lat = float(line[0:line.find(' ')])
        lon = float(line[line.find(' '):line.find('\n')])
        points[numPoints].update({'coord': (lat, lon)})
        numPoints += 1

    numPoints = 0

    timeFile.close()
    tempFile.close()
    phFile.close()
    oxyPercentFile.close()
    oxyMglFile.close()
    condFile.close()
    coordFile.close()

    return points