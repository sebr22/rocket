# SPDX-FileCopyrightText: 2020 by Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

#pip install Adafruit-Blinka
import datetime
import time
import board

#pip3 install adafruit-circuitpython-scd4x
import adafruit_scd4x

import busio

#sudo pip3 install adafruit-circuitpython-lps2x
import adafruit_lps2x

#sudo pip3 install adafruit-circuitpython-bh1750
import adafruit_bh1750

import threading

import csv
import asyncio

# GPS
import adafruit_gps
i2c = board.I2C()  
gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")
last_print = time.monotonic()
# END GPS

#CO2
i2cCO = board.I2C()
scd4x = adafruit_scd4x.SCD4X(i2cCO)
print("Serial number:", [hex(i) for i in scd4x.serial_number])

# FILE NAME
# str(time.time())
filen = str(time.time())
file = "csvs/"+filen+".csv"
fp = open(file, 'x')
fp.close()

#Pressure
i2cPress = busio.I2C(board.SCL, board.SDA)
lps = adafruit_lps2x.LPS25(i2cPress)

#Brightness
bhbrt = adafruit_bh1750.BH1750(i2c)

scd4x.start_periodic_measurement()
print("Waiting for first measurement....")

with open(file, mode='a') as list:
    data = csv.writer(list)
    data.writerow(["Date", "Brightness", "CO2", "Humidity", "Pressure", "Temperature", "Latitude", "Longitude", "Altitude","Speed","Track Angle","Horizontal Dilution","Height GeoID", "Fix Quality", "Num Satelites", "Latitude Degrees", "Latitude Minutes","Longitude Degrees","Longitude Minutes"])

dt = datetime.datetime.now()

co2 = scd4x.CO2
brt = bhbrt.lux
relhum = scd4x.relative_humidity 
press = lps.pressure
temp = lps.temperature 
lat = gps.latitude
lon = gps.longitude 
alt = gps.altitude_m 
spd = gps.speed_knots 
trk = gps.track_angle_deg 
hdil = gps.horizontal_dilution 
geo = gps.height_geoid 
fixq = gps.fix_quality 
numsats = gps.satellites 
latdeg = gps.latitude_degrees 
latmin = gps.latitude_minutes 
londeg = gps.longitude_degrees 
lonmin = gps.longitude_minutes

def update_gps(): 
    global lat, lon, alt, spd, trk, hdil, geo, fixq, numsats, latdeg, latmin, londeg, lonmin
    while True:
        gps.update()
        lat = gps.latitude
        lon = gps.longitude 
        alt = gps.altitude_m 
        spd = gps.speed_knots 
        trk = gps.track_angle_deg 
        hdil = gps.horizontal_dilution 
        geo = gps.height_geoid 
        fixq = gps.fix_quality 
        numsats = gps.satellites 
        latdeg = gps.latitude_degrees 
        latmin = gps.latitude_minutes 
        londeg = gps.longitude_degrees 
        lonmin = gps.longitude_minutes
        # print(lat)

def update_scd4x():
    global co2, relhum
    while True:
        if scd4x.data_ready:
            co2 = scd4x.CO2
            relhum = scd4x.relative_humidity 

def update_lps():
    global press, temp
    while True:
        press = lps.pressure
        temp = lps.temperature 

def update_bh1750():
    global brt
    while True:
        brt = bhbrt.lux

def add_csv():
    while True:
        print(datetime.datetime.now(), brt, co2, relhum, press, temp, lat, lon, alt, spd, trk, hdil, geo, fixq, numsats, latdeg, latmin, londeg, lonmin)
        # print(datetime.datetime.now(), brt, co2, relhum, press, temp)
        with open(file, mode='a') as list:
                data = csv.writer(list)
                data.writerow([datetime.datetime.now(), brt, co2, relhum, press, temp, lat, lon, alt, spd, trk, hdil, geo, fixq, numsats, latdeg, latmin, londeg, lonmin])
                # data.writerow([datetime.datetime.now(), brt, co2, relhum, press, temp])
        time.sleep(0.5)

tadd_csv = threading.Thread(target=add_csv)
tgps = threading.Thread(target=update_gps)
tscd4x = threading.Thread(target=update_scd4x)
tlps = threading.Thread(target=update_lps)
tbh1750 = threading.Thread(target=update_bh1750)

tgps.start()
tscd4x.start()
tlps.start()
tbh1750.start()
tadd_csv.start()

