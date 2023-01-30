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

import csv

#CO2
i2cCO = board.I2C()
scd4x = adafruit_scd4x.SCD4X(i2cCO)
print("Serial number:", [hex(i) for i in scd4x.serial_number])

# FILE NAME
file = str(time.time()) + ".csv"
fp = open(file, 'x')
fp.close()

#Pressure
i2cPress = busio.I2C(board.SCL, board.SDA)
lps = adafruit_lps2x.LPS25(i2cPress)

scd4x.start_periodic_measurement()
print("Waiting for first measurement....")

with open(file, mode='a') as list:
    data = csv.writer(list)
    data.writerow(["Date", "CO2", "Humidity", "Pressure", "Temperature"])

while True:
    if scd4x.data_ready:
        print("CO2: %d ppm" % scd4x.CO2)
        print("Humidity: %0.1f %%" % scd4x.relative_humidity)
        print("Pressure: %.2f hPa" % lps.pressure)
        print("Temperature: %.2f C" % lps.temperature)

        with open(file, mode='a') as list:
            data = csv.writer(list)
            data.writerow([datetime.datetime.now(), scd4x.CO2, scd4x.relative_humidity, lps.pressure, lps.temperature])

        print("\n \n")