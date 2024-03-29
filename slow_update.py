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
    data.writerow(["Date", "CO2", "Humidity", "Pressure", "Temperature", "Latitude", "Longitude", "Altitude","Speed","Track Angle","Horizontal Dilution","Height GeoID", "Fix Quality", "Num Satelites", "Latitude Degrees", "Latitude Minutes","Longitude Degrees","Longitude Minutes"])

# while True:


    # if scd4x.data_ready:
    #     print("CO2: %d ppm" % scd4x.CO2)
    #     print("Humidity: %0.1f %%" % scd4x.relative_humidity)
    #     print("Pressure: %.2f hPa" % lps.pressure)
    #     print("Temperature: %.2f C" % lps.temperature)

    #     with open(file, mode='a') as list:
    #         data = csv.writer(list)
    #         data.writerow([datetime.datetime.now(), scd4x.CO2, scd4x.relative_humidity, lps.pressure, lps.temperature])

    #     print("\n \n")

while True:
    if scd4x.data_ready:
        print("CO2: %d ppm" % scd4x.CO2)
        print("Humidity: %0.1f %%" % scd4x.relative_humidity)
        print("Pressure: %.2f hPa" % lps.pressure)
        print("Temperature: %.2f C" % lps.temperature)

        print("%.2f Lux"%bhbrt.lux)
        
        # Make sure to call gps.update() every loop iteration and at least twice
        # as fast as data comes from the GPS unit (usually every second).
        # This returns a bool that's true if it parsed new data (you can ignore it
        # though if you don't care and instead look at the has_fix property).
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
            print(gps.longitude)


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
            
            with open(file, mode='a') as list:
                data = csv.writer(list)
                data.writerow([datetime.datetime.now(), bhbrt.lux, scd4x.CO2, scd4x.relative_humidity, lps.pressure, lps.temperature, gps.latitude, gps.longitude, gps.altitude_m, gps.speed_knots, gps.track_angle_deg, gps.horizontal_dilution, gps.height_geoid, gps.fix_quality, gps.satellites, gps.latitude_degrees, gps.latitude_minutes,gps.longitude_degrees, gps.longitude_minutes])
            print("\n \n")
