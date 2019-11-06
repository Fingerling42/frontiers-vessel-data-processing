import folium
from folium import plugins
import map_module as mm
import grid_module as gm
import time

starTime = time.time()

## Get datapoins with fields: time, tempr, ph, oxy_percent, oxy_mgl, cond, coord
points = mm.get_data_points()

## Create a map
fmap = folium.Map(
    location = points[0].get('coord'),
    tiles = 'OpenStreetMap',
    zoom_start = 16
    )

## Create grid with choropleths
gridNum = 60                        ## Number of cells on one side, sum of cells — gridNum x gridNum
mapArea =  ((53.509200, 49.217000), 
            (53.503700, 49.226000))

[cells, squareSize] = gm.get_grid(points, mapArea, 'tempr', gridNum)
[choropleth, colormap] = gm.create_choropleth(cells, 'tempr', "Temperature, °C (cell diag = {sqsize:.2f} m)".format(sqsize=squareSize))
fmap.add_child(choropleth)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(choropleth, colormap))

[cells, squareSize] = gm.get_grid(points, mapArea, 'ph', gridNum)
[choropleth, colormap] = gm.create_choropleth(cells, 'ph', "pH level (cell diag = {sqsize:.2f} m)".format(sqsize=squareSize))
fmap.add_child(choropleth)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(choropleth, colormap))

[cells, squareSize] = gm.get_grid(points, mapArea, 'oxy_mgl', gridNum)
[choropleth, colormap] = gm.create_choropleth(cells, 'oxy_mgl', "Oxygen, mg/L (cell diag = {sqsize:.2f} m)".format(sqsize=squareSize))
fmap.add_child(choropleth)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(choropleth, colormap))

[cells, squareSize] = gm.get_grid(points, mapArea, 'cond', gridNum)
[choropleth, colormap] = gm.create_choropleth(cells, 'cond', "Electrical conductivity, uS / cm (cell diag = {sqsize:.2f} m)".format(sqsize=squareSize))
fmap.add_child(choropleth)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(choropleth, colormap))

## Draw real GPS path
fgvPath = folium.FeatureGroup(name='path', show=True)

folium.PolyLine(
    [[x['coord'][0], x['coord'][1]] for x in points], 
    color="black", 
    weight=5, 
    opacity=1
    ).add_to(fgvPath)

folium.Marker(
    points[0].get('coord'),
    icon=folium.Icon(color='green'),
    tooltip='Start',
    ).add_to(fgvPath)

folium.Marker(
    points[len(points)-1].get('coord'),
    tooltip='End',
    icon=folium.Icon(color='red'),
    ).add_to(fgvPath)

fmap.add_child(fgvPath)

## Draw planned GPS path
planPath = []

with open('../coordinates_plan.txt', 'r') as geoPlan:
    for line in geoPlan:
        lat = float(line[0:line.find(' ')])
        lon = float(line[line.find(' '):line.find('\n')])
        planPath.append([lat, lon])


fgvPath = folium.FeatureGroup(name='plan', show=False)

folium.PolyLine(
    planPath, 
    color="white", 
    weight=5,
    opacity=1
    ).add_to(fgvPath)

folium.Marker(
    planPath[0],
    icon=folium.Icon(color='green'),
    tooltip='Start',
    ).add_to(fgvPath)

folium.Marker(
    planPath[len(planPath)-1],
    icon=folium.Icon(color='red'),
    tooltip='End',
    ).add_to(fgvPath)

fmap.add_child(fgvPath)

## Add laver control 
fmap.add_child(folium.map.LayerControl())

## Create HTML-file
fmap.save("grid-map-4-25-2019.html")

endTime = time.time()

print('--- Elapsed time: {:.2f} sec ---'.format(endTime - starTime))