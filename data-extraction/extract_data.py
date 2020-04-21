## Script for extract data and coordinates from logs
## Logs are formed without chaotic beginning, just smooth meander

import support_module as sm

## Preparing: extract meaningful geo data and remove redundant data before 751th line
sm.delete_first_lines()
sm.adduct_data()
sm.remove_beginning(751)

points = []
numPoints = 0

## Extract sensing points with data

with open('logs_smooth.txt') as measData:
    for line in measData:
        # Extract time
        points.append(dict(time=int(line[0:10])))

        # Extract temperature
        indexS = line.find('WT:') + 3
        indexE = line.find('#PH:')
        points[numPoints].update({'tempr': float(line[indexS:indexE])})

        # Extract pH
        indexS = line.find('PH:') + 3
        indexE = line.find('#DO:')
        points[numPoints].update({'ph': float(line[indexS:indexE])})

        # Extract oxygen in percentage
        indexS = line.find('#DO:') + 4
        indexE = line.find('#COND:')
        points[numPoints].update({'oxy_percent': float(line[indexS:indexE])})

        # Extract electrical conductivity
        indexS = line.find('#COND:') + 6
        indexE = len(line) - 2
        points[numPoints].update({'cond': float(line[indexS:indexE])})

        numPoints += 1


## Convert percentage of oxygen to mg / l
## Fuction takes list of temperature and list of oxygen
oxyConc = sm.oxy_convert([d['tempr'] for d in points], [d['oxy_percent'] for d in points])

for i in range(0, len(points)):
    points[i].update({'oxy_mgl': oxyConc[i]})

## Extract coords from file with meaningful coordinates
numPoints = 0

with open('geo_meaningful_smooth.txt') as geoData:
    for line in geoData:
        geoTime = int(line[0:10])

        indexS = line.find('lat : ') + 6
        indexE = line.find(', lon')
        lat = float(line[indexS:indexE]) / 10 ** 7

        indexS = line.find('lon : ') + 6
        indexE = line.find(', alt')
        lon = float(line[indexS:indexE]) / 10 ** 7

        points[numPoints].update({'coord': (lat, lon)})

        numPoints += 1

## Extract real coords from file with planned coordinates
planPath = []

with open('path_smooth.waypoints', 'r') as geoPlan:
    for line in geoPlan:
        index = line.find('53.')
        lat = float(line[index:(index + 11)])
        index = line.find('49.')
        lon = float(line[index:(index + 11)])
        pathCoord = [lat, lon]
        planPath.append(pathCoord)

## Write data to files
timeFile = open('../times.txt', 'w')
tempFile = open('../temperature.txt', 'w')
phFile = open('../phs.txt', 'w')
oxyPercentFile = open('../oxygen_percent.txt', 'w')
oxyMglFile = open('../oxygen_mgl.txt', 'w')
condFile = open('../conductivity.txt', 'w')
coordFile = open('../coordinates_real.txt', 'w')
coordRealFile = open('../coordinates_plan.txt', 'w')

for i in range(0, numPoints):
    timeFile.write('{:.0f}'.format((points[i]['time'] - points[0]['time'])) + '\n')
    tempFile.write('{:.2f}'.format(points[i]['tempr']) + '\n')
    phFile.write('{:.2f}'.format(points[i]['ph']) + '\n')
    oxyPercentFile.write('{:.1f}'.format(points[i]['oxy_percent']) + '\n')
    oxyMglFile.write('{:.1f}'.format(points[i]['oxy_mgl']) + '\n')
    condFile.write('{:.1f}'.format(points[i]['cond']) + '\n')
    coordFile.write('{:.7f} {:.7f}'.format(points[i]['coord'][0], points[i]['coord'][1]) + '\n')

for i in range(0, len(planPath)):
    coordRealFile.write('{:.7f} {:.7f}'.format(planPath[i][0], planPath[i][1]) + '\n')

timeFile.close()
tempFile.close()
phFile.close()
oxyPercentFile.close()
oxyMglFile.close()
condFile.close()
coordFile.close()
coordRealFile.close()