# bno055_test.py Simple test program for MicroPython bno055 driver

# Copyright (c) Peter Hinch 2019
# Released under the MIT licence.

# Adafruit Feather
# https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/pinouts

# Adafruit Python BNO055 driver
# https://github.com/adafruit/Adafruit_Python_BNO055/blob/master/Adafruit_BNO055/BNO055.py

# Adafruit CircuitPython BNO055 driver
# https://github.com/adafruit/Adafruit_CircuitPython_BNO055/blob/master/adafruit_bno055.py

# Peter's MicroPython adapted driver
# https://github.com/micropython-IMU/micropython-bno055/tree/master

# BNO055 Reference
# https://ae-bst.resource.bosch.com/media/_tech/media/application_notes/BST-BNO055-AN012.pdf
# https://ae-bst.resource.bosch.com/media/_tech/media/datasheets/BST-BNO055-DS000.pdf

# Micropython ESP32 Reference
# https://docs.micropython.org/en/latest/esp32/quickref.html#

import utime
import machine
import network

from bno055 import *

import usocket

i2c = machine.I2C(0, scl=machine.Pin(32), sda=machine.Pin(33))
imu = BNO055(i2c=i2c, address=0x29) # 0x29 or 0x28

ser = machine.UART(2, baudrate=115200, bits=8, parity=None, stop=1, tx=17, rx=16, timeout=100)
#imu = BNO055(serial=ser)

calibrated = False

machine.freq(240000000)
print('CPU Speed: ' + str(machine.freq()))

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("Tomato24", "Stephen123")
print("Waiting for connection...")
while not sta_if.isconnected():
    utime.sleep(1)
print(sta_if.ifconfig())

utime.sleep(5)

s = usocket.socket()
addr = usocket.getaddrinfo('192.168.1.112', 61111, 0, usocket.SOCK_STREAM)[0][-1]

quat = bytes(8)
while True:
    utime.sleep_ms(5) 
    #time.sleep(1)
#    if not calibrated:
#        calibrated = imu.calibrated()
#        print('Calibration required: sys {} gyro {} accel {} mag {}'.format(*imu.cal_status()))
#    print('Temperature {}°C'.format(imu.temperature()))
#    print('Mag       x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.mag()))
#    print('Gyro      x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.gyro()))
#    print('Accel     x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.accel()))
#    print('Lin acc.  x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.lin_acc()))
#    print('Gravity   x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.gravity()))
    #euler = imu.euler()
    #print('Heading     {:4.0f} roll {:4.0f} pitch {:4.0f}'.format(*euler))
    
    quat = imu.raw_quaternion(quat)

    
    print(quat)
    try:
        s.send(quat)
    except OSError:
        s = usocket.socket()
        print("Reconnecting...")
        connected = False
        while not connected:
            try:
                s.connect(addr)
                connected = True
                print("Connected")
            except OSError:
                utime.sleep(2) 
    

