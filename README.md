# Install MicroPython
Follow instructions at:<br/>
https://docs.micropython.org/en/latest/esp32/tutorial/intro.html

- download firmware
- install esptool: pip install esptool --user
- erase flash: 
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
- flash: 
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ~/Downloads/esp32-idf4-20191220-v1.12.bin

Install rshell<br/>
pip3 install rshell --user

Sync src folder to board<br/>
rshell -p /dev/ttyUSB0 rsync src /pyboard

Monitor<br/>
rshell -p /dev/ttyUSB0 -e nano repl

# References

Adafruit Python BNO055 driver
https://github.com/adafruit/Adafruit_Python_BNO055/blob/master/Adafruit_BNO055/BNO055.py

Adafruit CircuitPython BNO055 driver
https://github.com/adafruit/Adafruit_CircuitPython_BNO055/blob/master/adafruit_bno055.py

Peter's MicroPython adapted driver
https://github.com/micropython-IMU/micropython-bno055/tree/master

BNO055 Reference
https://ae-bst.resource.bosch.com/media/_tech/media/application_notes/BST-BNO055-AN012.pdf
https://ae-bst.resource.bosch.com/media/_tech/media/datasheets/BST-BNO055-DS000.pdf

Micropython ESP32 Reference
https://docs.micropython.org/en/latest/esp32/quickref.html#
