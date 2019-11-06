import folium
from folium import plugins
import map_module as mm
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

## Draw sensor data with colorization and colormap legend
[fgv, segment] = mm.draw_points_group(points, 'tempr', 'Temperature', False)
colormap = mm.create_colormap(segment, 'Temperature, °C')
fmap.add_child(fgv)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(fgv, colormap))

[fgv, segment] = mm.draw_points_group(points, 'ph', 'pH', True)
colormap = mm.create_colormap(segment, 'pH level')
fmap.add_child(fgv)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(fgv, colormap))

[fgv, segment] = mm.draw_points_group(points, 'oxy_mgl', 'Oxygen', False)
colormap = mm.create_colormap(segment, 'Oxygen, mg / l')
fmap.add_child(fgv)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(fgv, colormap))

[fgv, segment] = mm.draw_points_group(points, 'cond', 'Electrical conductivity', False)
colormap = mm.create_colormap(segment, 'Electrical conductivity, uS / cm')
fmap.add_child(fgv)
fmap.add_child(colormap)
fmap.add_child(mm.bind_colormap(fgv, colormap))

## Draw real GPS path
fgvPath = folium.FeatureGroup(name='Path', show=False)

folium.PolyLine(
    [[x['coord'][0], x['coord'][1]] for x in points], 
    color="red", 
    weight=2.5, 
    opacity=1
    ).add_to(fgvPath)

folium.Marker(
    points[0].get('coord'),
    icon=folium.Icon(color='green'),
    tooltip='Start',
    ).add_to(fgvPath)

folium.Marker(
    points[len(points)-1].get('coord'),
    icon=folium.Icon(color='red'),
    tooltip='End',
    ).add_to(fgvPath)

fmap.add_child(fgvPath)

## Add laver control 
fmap.add_child(folium.map.LayerControl())

## Create HTML-file
fmap.save("dot-map-4-25-2019.html")

endTime = time.time()

print('--- Elapsed time: {:.2f} sec ---'.format(endTime - starTime))