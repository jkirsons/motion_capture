# ESP32 Motion Capture Sensor Firmware 
This configures an ESP32 as a hub, connected with up to 4 BNO055 IMUs.  The IMUs are connected to both I2C buses using their default addresses 0x28 and 0x29.

## Initial Starup
When first powered on, the ESP32 sets up an AP:<br>
<b>ssid:</b> SensorWiFi<br>
<b>password:</b> password123<br>
The LED will be solid on when the AP is waiting for configuration settings.

Connect to this AP, and configure the WiFi settings, and the IP of the machine running the Blender plugin.

## Running Mode
Once the ESP32 hub starts, it:
- Connects to the configured WiFi AP (LED flashes once after connected)
- Connects to the Blender PC, and starts sending sensor data (LED flashes once for every 100 frames sent)
- If no connection to the Blender PC can be made in 60 seconds, the ESP32 goes back into AP configuration mode. (And LED is solid on again)
- If you reset the ESP32, it will try connecting to the WiFi and Blender PC again with the saved details again.

# Installing MicroPython
Follow instructions at:<br/>
https://docs.micropython.org/en/latest/esp32/tutorial/intro.html

- download firmware
- install esptool: pip install esptool --user
- erase flash: esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
- flash: esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ~/Downloads/esp32-idf4-version.bin

Install rshell<br/>
pip3 install rshell --user

Sync src folder to board<br/>
rshell -p /dev/ttyUSB0 rsync src /pyboard

Monitor<br/>
rshell -p /dev/ttyUSB0 -e nano repl

Or see tasks.json

# References

Adafruit Python BNO055 driver<br/>
https://github.com/adafruit/Adafruit_Python_BNO055/blob/master/Adafruit_BNO055/BNO055.py

Adafruit CircuitPython BNO055 driver<br/>
https://github.com/adafruit/Adafruit_CircuitPython_BNO055/blob/master/adafruit_bno055.py

Peter's MicroPython adapted driver<br/>
https://github.com/micropython-IMU/micropython-bno055/tree/master

BNO055 Reference<br/>
https://ae-bst.resource.bosch.com/media/_tech/media/application_notes/BST-BNO055-AN012.pdf
https://ae-bst.resource.bosch.com/media/_tech/media/datasheets/BST-BNO055-DS000.pdf

Micropython ESP32 Reference<br/>
https://docs.micropython.org/en/latest/esp32/quickref.html#

WiFi Manager<br/>
https://randomnerdtutorials.com/micropython-wi-fi-manager-esp32-esp8266/
