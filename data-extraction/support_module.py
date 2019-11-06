## Module with support functions

def rd(x,y=0):
## A classical mathematical rounding by Voznica
    m = int('1'+'0'*y) # multiplier - how many positions to the right
    q = x*m # shift to the right by multiplier
    c = int(q) # new number
    i = int( (q-c)*10 ) # indicator number on the right
    if i >= 5:
        c += 1
    return c/m

def oxy_convert(tempData, oxyData):
## Convert oxygen from percentage to mg / l

    # max temperature = 7.79
    # min temperature = 4.94

    def temp_comparison(temp, table):
        for i in range(0, len(table)):
            if temp == table[i]['tempNorm']:
                oxyTrue = table[i]['oxyNorm']
        return oxyTrue

    ## Pressure values in Pa
    ## Actual value on measurement day (04.25.19) — 755 mm Hg (https://www.gismeteo.ru/diary/4429/2019/4/)
    pressureNorm = 101325
    pressureActual = 100658

    oxyNormTable = []
    numTable = 0

    ## Table of normal concentration from min to max temperature
    with open('oxy_norm_concentration.txt', 'r') as f:
        for line in f:
            tempNorm = float(line[0:line.find('#')])
            oxyNormTable.append(dict(tempNorm=tempNorm))
            oxyNorm =  float(line[(line.find('#') + 1):len(line)])
            oxyNormTable[numTable].update({'oxyNorm': oxyNorm})
            numTable += 1

    oxyConcList = []

    for i in range(0, len(tempData)):

        temp = rd(tempData[i], 1)
        oxyPercent = rd(oxyData[i], 1)

        oxyNorm = temp_comparison(temp, oxyNormTable)

        oxyConc = oxyPercent * oxyNorm * pressureActual / (100 * pressureNorm)

        oxyConcList.append(rd(oxyConc, 2))

    return oxyConcList


def remove_beginning(lineNum):
## Delete first lineNum lines
## First lines dob't constitute the meander

    geoData = open('geo_meaningful_smooth.txt', 'w')
    logData = open('logs_smooth.txt', 'w')

    lineCount = 1
    with open('geo_meaningful.txt') as file:
        for line in file:
            if lineCount < lineNum:
                lineCount += 1
            else:
                geoData.write(line)

    geoData.close()

    lineCount = 1
    with open('logs_original.txt') as file:
        for line in file:
            if lineCount < lineNum:
                lineCount += 1
            else:
                logData.write(line)

    logData.close()

def line_avg(line1, line2):
## Function for formation of new line 
## from average values of prev and next lines.

    lines = [line1, line2]

    line = []

    # Find keys in lines and add it to dicts

    for i in range(2):
        indexE = lines[i].find(' GLOBAL')
        line.append(dict(time=float(lines[i][0:indexE])))

        indexS = lines[i].find('time_boot_ms : ') + 15
        indexE = lines[i].find(', lat :')
        line[i].update({'time_boot_ms': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('lat : ') + 6
        indexE = lines[i].find(', lon')
        line[i].update({'lat': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('lon : ') + 6
        indexE = lines[i].find(', alt')
        line[i].update({'lon': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('alt : ') + 6
        indexE = lines[i].find(', relative_alt')
        line[i].update({'alt': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('relative_alt : ') + 15
        indexE = lines[i].find(', vx :')
        line[i].update({'relative_alt': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('vx : ') + 5
        indexE = lines[i].find(', vy :')
        line[i].update({'vx': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('vy : ') + 5
        indexE = lines[i].find(', vz :')
        line[i].update({'vy': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('vz : ') + 5
        indexE = lines[i].find(', hdg :')
        line[i].update({'vz': int(lines[i][indexS:indexE])})

        indexS = lines[i].find('hdg : ') + 6
        indexE = len(lines[i]) - 2
        line[i].update({'hdg': int(lines[i][indexS:indexE])})

    # Form avg keys

    time = (line[0].get('time') + line[1].get('time')) / 2
    timeBoot = int((line[0].get('time_boot_ms') + line[1].get('time_boot_ms')) / 2)
    lat = int((line[0].get('lat') + line[1].get('lat')) / 2)
    lon = int((line[0].get('lon') + line[1].get('lon')) / 2)
    alt = int((line[0].get('alt') + line[1].get('alt')) / 2)
    rAlt = int((line[0].get('relative_alt') + line[1].get('relative_alt')) / 2)
    vx = int((line[0].get('vx') + line[1].get('vx')) / 2)
    vy = int((line[0].get('vy') + line[1].get('vy')) / 2)
    vz = int((line[0].get('vz') + line[1].get('vz')) / 2)
    hdg = int((line[0].get('hdg') + line[1].get('hdg')) / 2)

    # Form new line

    avgLine = '{time:.6f} GLOBAL_POSITION_INT {{time_boot_ms : {timeBoot}, lat : {lat}, lon : {lon}, alt : {alt}, relative_alt : {rAlt}, vx : {vx}, vy : {vy}, vz : {vz}, hdg : {hdg}}}\n'.format(
        time=time, 
        timeBoot=timeBoot, 
        lat=lat,
        lon=lon,
        alt=alt,
        rAlt=rAlt,
        vx=vx,
        vy=vy,
        vz=vz,
        hdg=hdg)

    return avgLine

def adduct_data():
## Function for comparing logs of measurements and geodata.
## It selects geodata for existing measurements only.
    
    log = open('logs_original.txt', 'r')
    geoData = open('geo_original.txt', 'r')
    geoResult = open('geo_meaningful.txt', 'w')

    lineLog = log.readline()

    count = 0

    for lineGeo in geoData:
        # If logs reached EOF, break
        if lineLog == '':
            break

        # Extract UNIX-time from lines
        timeLog = int(lineLog[0:10])
        timeGeo = int(lineGeo[0:10])

        # Compare time 
        if timeLog == timeGeo:
            geoResult.write(lineGeo)
            lineLog = log.readline()
        # Some ticks in geodata is missed, form new geodata from prev and next records
        elif timeLog < timeGeo:
            newLine = line_avg(lineGeoPrv, lineGeo)
            geoResult.write(newLine)
            lineLog = log.readline()
        else:
            pass

        lineGeoPrv = lineGeo

    log.close()
    geoData.close()
    geoResult.close()