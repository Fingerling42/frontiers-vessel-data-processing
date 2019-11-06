### Module for generate_grid_map.py.
import math
import geojson
import pandas
import branca
import folium

def get_square(upperLeft, lowerRight):
    """
    Generates 4 geo coordinates of a square from the coordinates of the upper left and lower right corners.

    Parameters
    ----------
    upperLeft   : tuple of floats
        The geo coordinates of upper left corner in form (lat, lon).

    lowerRight  : tuple of floats
        The geo coordinates of lower right corner in form (lat, lon).

    Returns
    ----------
    tuple of tuples
        Tuple of four geo coordinates in form (lat, lon). Corner order: upper left, upper right, upper left,
        lower right, lower left.
    """

    square = (upperLeft, (upperLeft[0], lowerRight[1]), lowerRight,(lowerRight[0], upperLeft[1]))
    return square



def check_point(pointCoord, upperLeft, lowerRight):
    """
    Checks if a point is within a square.

    Parameters
    ----------
    pointCoord  : tuple of floats
        The geo coordinates of point in form (lat, lon).

    upperLeft   : tuple of floats
        The geo coordinates of upper left square corner in form (lat, lon).

    lowerRight  : tuple of floats
        The geo coordinates of lower right square corner in form (lat, lon).

    Returns
    ----------
    bool
        True if point is within, otherwise - False.
    """

    if lowerRight[0] <= pointCoord[0] <= upperLeft[0] and upperLeft[1] <= pointCoord[1] <= lowerRight[1]:
        return True
    else:
        return False



def get_grid(points, area, sample, gridNum):
    """
    Forms a grid of a given size on a given area according to measurement data. For each grid cell in which 
    the data points fall, the average value of the index is calculated. 

    Parameters
    ----------
    points              : list of dicts
        All measurement points with time, coordinates and results. For each point there are the following keys:
        'time'          : float
        'coord'         : tuple of floats
        'tempr'         : float
        'ph'            : float
        'oxy_percent'   : float
        'oxy_mgl'       : float
        'cond'          : float

    area        : tuple of tuples 
        Tuple of geo coordinates of upper left and lower right grid area corners in form (lat, lon).

    sample      : string
        The key for point structure, that describes the desired measurement data array.

    gridNum     : interger
        Grid dimensions gridNum × gridNum

    Returns
    ----------
    list of dicts
        All cells in which points fell. For each cell there are the following keys:
        'sqCoord'   : tuple of tuples   --- Four cell coordinates
        'avgSum'    : float             --- Sum of measurement result
        'avgCountr' : interger          --- Number of points in cell
        'avg'       : float             --- Averege measurement result in cell

    float
        Size of cell side in meters
    """

    ## Find grid spacing from size of map area.
    upperLeft   = area[0]
    lowerRight  = area[1]
    incLat = (upperLeft[0] - lowerRight[0]) / gridNum
    incLon = (lowerRight[1] - upperLeft[1]) / gridNum


    ## Generate grid
    cells = []
    numCell = 0
    for i in range(0, gridNum):
        for j in range(0, gridNum):
            cellUpLeft = (upperLeft[0] - j * incLat, upperLeft[1] + i * incLon) # upper left cornet of cell
            cellLowRight = (cellUpLeft[0] - incLat, cellUpLeft[1] + incLon)     # lower right cornet of cell

            cells.append(dict(sqCoord=get_square(cellUpLeft, cellLowRight)))
            cells[numCell].update({'avgSum': 0.0})
            cells[numCell].update({'avgCountr': 0})
            numCell += 1

    ## Find averege measurement result for cell
    cellsWorth = []
    cellsWorthNum = 0
    for i in range(0, numCell):
        for point in points:
            if check_point(point.get('coord'), cells[i]['sqCoord'][0], cells[i]['sqCoord'][2]):
                cells[i]['avgSum'] += point[sample]
                cells[i]['avgCountr'] += 1

        ## Discard empty cells
        if cells[i]['avgCountr'] != 0:
            cellsWorth.append(cells[i])
            cellsWorth[cellsWorthNum].update({'avg': cells[i]['avgSum'] / cells[i]['avgCountr']})
            cellsWorthNum += 1

    ## Find cell size in meters
    earthRad = 6371 * 10 ** 3   # radius of Earth

    # Transform from degrees to radians
    tet1 = math.radians(cells[0]['sqCoord'][0][0])
    tet2 = math.radians(cells[0]['sqCoord'][2][0])
    fi1 = math.radians(cells[0]['sqCoord'][0][1])
    fi2 = math.radians(cells[0]['sqCoord'][2][1])

    cellSize = earthRad * math.acos(math.sin(tet1) * math.sin(tet2) + math.cos(tet1) * math.cos(tet2) * math.cos(fi1 - fi2))

    return cellsWorth, cellSize



def create_choropleth(cells, param, caption):

    palette = [ '#8800f8', # purple
                '#0010ff', # blue
                '#007fff', # azure
                '#00f8ff', # cyan
                '#00ff99', # spring
                '#00ff07', # green
                '#78ff00', # lime
                '#fff800', # yellow
                '#ff8000', # orange
                '#ff0a00'] # red

    ## Create geojson with cells coordinate and pandas dataframe with measurements
    cellsFeature = []
    dataDict = {'ID': [], 'Value': []}

    for i in range(0, len(cells)):
        # Create geojson polygon
        polygon = []
        for j in range(0, 4):                                               # Four coordinate of cells in list form
            polygon.append([cells[i]['sqCoord'][j][1], 
                            cells[i]['sqCoord'][j][0]])
        polygon.append([cells[i]['sqCoord'][0][1], 
                        cells[i]['sqCoord'][0][0]])                         # Repeat first coordinate to complete the polygon
        polygonJson = geojson.Polygon([polygon])                            # List brackets are important!
        # Create geojson features with ID of polygons
        cellsFeature.append(geojson.Feature(geometry=polygonJson, id=i, properties={param: '{val:.2f}'.format(val=cells[i]['avg'])}))

        # Create dict with ID and measurement Value for pandas dataframe
        dataDict['ID'].append(i)
        dataDict['Value'].append(cells[i]['avg'])

    # Create geojson feature collection and dump results
    cellsCollection = geojson.FeatureCollection(cellsFeature)
    cellsJson = geojson.dumps(cellsCollection)

    ## Create pandas dataframe and find min and max
    dataPandas = pandas.DataFrame(data=dataDict).set_index('ID')['Value']
    minIndex = min(dataPandas)
    maxIndex = max(dataPandas)

    ## Create colormap
    colormap = branca.colormap.LinearColormap(palette, vmin=minIndex, vmax=maxIndex)
    colormap = colormap.to_step(len(palette))
    colormap.caption = caption


    ## Create tooltip with data
    dataTooltip = folium.features.GeoJsonTooltip(   fields=[param], 
                                                    aliases=['{param}: '.format(param=param)]
                                                    )

    ## Create choropleth
    choropleth = folium.GeoJson(
                                cellsJson,
                                name=param,
                                tooltip=dataTooltip,
                                show=False,
                                style_function=lambda feature: {
                                    'fillColor': colormap(dataPandas[feature['id']]),
                                    'stroke' : True,
                                    'color' : 'black',
                                    'weight' : 1,
                                    'fillOpacity' : 0.8,
                                }
                                )

    return choropleth, colormap