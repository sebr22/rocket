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

#sudo pip3 install adafruit-circuitpython-gps
import adafruit_gps
import serial

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

#gps
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")


scd4x.start_periodic_measurement()
print("Waiting for first measurement....")

with open(file, mode='a') as list:
    data = csv.writer(list)
    data.writerow(["Date", "CO2", "Humidity", "Pressure", "Temperature"])

while True:
    if scd4x.data_ready:
        #gps
        gps.update()
        # Every second print out current location details if there's a fix.
        current = time.monotonic()
        if current - last_print >= 1.0:
            last_print = current
            if not gps.has_fix:
                # Try again if we don't have a fix yet.
                print("Waiting for fix...")
                continue
            # We have a fix! (gps.has_fix is true)
            # Print out details about the fix like location, date, etc.
            print("=" * 40)  # Print a separator line.
            print(
                "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                    gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                    gps.timestamp_utc.tm_mday,  # struct_time object that holds
                    gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                    gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                    gps.timestamp_utc.tm_min,  # month!
                    gps.timestamp_utc.tm_sec,
                )
            )
            print("Latitude: {0:.6f} degrees".format(gps.latitude))
            print("Longitude: {0:.6f} degrees".format(gps.longitude))
            print(
                "Precise Latitude: {:2.}{:2.4f} degrees".format(
                    gps.latitude_degrees, gps.latitude_minutes
                )
            )
            print(
                "Precise Longitude: {:2.}{:2.4f} degrees".format(
                    gps.longitude_degrees, gps.longitude_minutes
                )
            )
            print("Fix quality: {}".format(gps.fix_quality))
            # Some attributes beyond latitude, longitude and timestamp are optional
            # and might not be present.  Check if they're None before trying to use!
            if gps.satellites is not None:
                print("# satellites: {}".format(gps.satellites))
            if gps.altitude_m is not None:
                print("Altitude: {} meters".format(gps.altitude_m))
            if gps.speed_knots is not None:
                print("Speed: {} knots".format(gps.speed_knots))
            if gps.track_angle_deg is not None:
                print("Track angle: {} degrees".format(gps.track_angle_deg))
            if gps.horizontal_dilution is not None:
                print("Horizontal dilution: {}".format(gps.horizontal_dilution))
            if gps.height_geoid is not None:
                print("Height geoid: {} meters".format(gps.height_geoid))
        #end gps
        print("CO2: %d ppm" % scd4x.CO2)
        print("Humidity: %0.1f %%" % scd4x.relative_humidity)
        print("Pressure: %.2f hPa" % lps.pressure)
        print("Temperature: %.2f C" % lps.temperature)

        with open(file, mode='a') as list:
            data = csv.writer(list)
            data.writerow([datetime.datetime.now(), scd4x.CO2, scd4x.relative_humidity, lps.pressure, lps.temperature])

        print("\n \n")