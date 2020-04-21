# Marine Vessel Data Processing

This repository is dedicated to the processing and visualization of environmental data obtained during the experiment with a water drone equipped with sensors.

**Language:** Python

## Explanation of Repository

The repository contains:

* **data-extraction** — a directory for the raw data extraction and processing to readable format:
    * *extract_data.py* — a script for extract data and coordinates from logs.
    * *support_module.py* — a module with support functions for *extract_data.py*.
    * geo_original.txt, logs_original.txt — the data from the vessel (you can get the same data from IPFS, see **Experiment Description**).
    *  oxy_norm_concentration.txt — table for the conversion of oxygen from % to mg / l.
    * path_original.waypoints, path_smooth.waypoints — user defined waypoints.
* **data-mapping** — a directory for data visualization into map:
    * *generate_dot_map.py* — a script for generating measurement points on the map.
    * *generate_grid_map.py* — a script for generating сhoropleth on the map.
    * *grid_module.py*, *map_module.py* — modules with support functions for scripts.
* **example-maps** — a directory with examples of generated maps.
    * dot-map-4-25-2019.html — a map with dots in html format.
    * grid-map-4-25-2019.html — a map with сhoropleth in html format.

## Prerequisites
You need [Python 3.x](https://www.python.org) and this packages:
* [folium](https://python-visualization.github.io/folium/) — mapping.
* [pandas](https://pandas.pydata.org/) — data processing and analysis.
* [geojson](https://pypi.org/project/geojson/) — format for storing geodata.
* [numpy](https://numpy.org/) — math functions.

## Installation and Launch
1. Clone the repository:
```
$ git clone https://github.com/Fingerling42/frontiers-vessel-data-processing.git
```
2. To get data from raw logs, launch:
```
$ python ./data-extraction/extract_data.py
```
This generates txt files in the root directory with with data for each water indicator as well as some auxiliary txt files in the **data-extraction** directory.

3. To create a map with measurement points, launch:
```
$ python ./data-mapping/generate_dot_map.py
```
To create a map with a сhoropleth, launch:
```
$ python ./data-mapping/generate_grid_map.py
```
Both scripts create html files with the measurement results plotted on a map.

4. To view the results, open the html files in any Internet browser.

## Experiment Description
Experiments [took place](https://goo.gl/maps/NR6VHbbRvRjM5mQ26) in Volga river in Kuibyshev reservoir near storm drains of Avtozavodsky district, Togliatti, Samara region, Russia.

Date and time (local time — GMT+4):
* Beginning — 4/25/2019, 7:12:52 PM
* Ending — 4/25/2019, 9:46:30 PM

Total measurement time: 154 minutes.

Measured parameters:
* temperature, ˚С;
* pH indicator;
* dissolved oxygen, %;
* electrical conductivity, µS / cm

Depth of measurements: 1,5-2 m.


The collected measurement and GPS logs were sent by the vessel to the IPFS network, and also saved locally on the SD card.  They are available in IPFS at these links: [sensor data](https://gateway.ipfs.io/ipfs/QmWRjFcQi4Xcisqi8FP3AbGS3PB3gNHgtnfzbcpodKKCBP) and [geodata](https://gateway.ipfs.io/ipfs/QmPvULEGfDE2Roscy4zGpKpBE8s3sBwjiXJVQNS3sBxWDC).

An example of a geodata log:
```
1556199326.265429 GLOBAL_POSITION_INT {time_boot_ms : 14730655, lat : 535077162, lon : 492266213, alt : 54310, relative_alt : 310, vx : -56, vy : -26, vz : 0, hdg : 27423}
```
An example of a measurement log:
```
1556199372.384576 <=>\x86##5E1567057C105409#DOV01SW#0#WT:6.53#PH:8.89#DO:90.4#COND:348.9#
```
## Data Processing

First, significant data was extracted from the logs. Measurements and GPS coordinates were recorded discretely, and measurements took place over longer periods of time. Therefore, it was necessary to reduce this data into one structure, choosing from GPS only those coordinates that corresponded to the sensor logs. Reducing was done using UNIX timestamps (you can see it in geo_meaningful.txt after launching the script). Also, the actual experimental data (without initial check of sensors) was extracted into separate files (geo_meaningful_smooth.txt, logs_smooth.txt). In the process, it turned out that for some measurement records there is no corresponding coordinate record. For this reason, the missing coordinates were interpolated using neighboring values.

After extracting the data on the concentration of oxygen in water, it became clear that the representation of oxygen in percentage terms is not enough for an adequate analysis of water quality, since in most cases it is necessary to convert the oxygen concentration in mg / l.  Such a conversion is nontrivial, because it requires knowledge of the water temperature, normal oxygen concentration at normal atmospheric pressure at a given temperature, and atmospheric pressure in a given area. A function `oxy_convert(tempData, oxyData)` was formed for oxygen conversion.

For visual representation of the extracted data, it was decided to display the data directly on the map, with reference to the coordinates.  At the first visualization, all the obtained values of parameters were sorted into 10 intervals, and color was assigned to each interval.

The second visualization is a сhoropleth. The choropleth requires a certain set of limited areas within which the intensity of an indicator will be calculated. To do this, the entire area was divided into a grid with a given number of segments and for each segment the average value of the points that entered it was considered. Then the segments were also sorted into 10 intervals.

## Acknowledgments

We want to thank the [Airalab team](https://aira.life/en/) for the development and support of the unmanned surface vessel, as well as for providing the Robonomics platform support and related software.