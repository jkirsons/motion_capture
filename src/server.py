# Released under the MIT licence.
import time
import machine
import network

import usocket
from sensors import sensors
import wifimgr

def run():
    machine.freq(160000000)
    print('Machine ID: ' + str(machine.unique_id()))
    print('CPU Speed: ' + str(machine.freq()))
    print("Starting WiFi")

    led = machine.Pin(2, machine.Pin.OUT)
    wlan = wifimgr.get_connection(led)

    # sta_if = network.WLAN(network.STA_IF)
    # sta_if.active(True)

    # print("Connecting WiFi")
    # sta_if.connect("WiFiSSID", "pass123")
    # while not sta_if.isconnected():
    #     machine.idle()
    # print(sta_if.ifconfig())

    addr = usocket.getaddrinfo(wifimgr.hostip, 61111, 0, usocket.SOCK_STREAM)[0][-1]

    led.value(1)
    time.sleep_ms(300)
    led.value(0)

    sens = sensors([27, 25, 17, 16])
    sens.scan()

    frame = 0
    first = True
    ledStatus = False
    
    s = usocket.socket()
    #s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)

    while True:
        #machine.lightsleep(10)
        if sens.connected_imus == 1:
            time.sleep_ms(5)
        elif sens.connected_imus == 2:
            time.sleep_ms(5)
        elif sens.connected_imus == 3:
            time.sleep_ms(2)
        elif sens.connected_imus == 4:
            time.sleep_ms(2)
        else:
            print("No IMUs connected!")

        #time.sleep_ms(5)
        # Get the machine id on first loop
        if first:
            sens.read_id()
            first = False
        else:
            sens.read_data()

        # Send the data
        try:
            for data in sens.data_list:
                s.send(data)

            frame += 1

            if frame % 100 == 0:
                ledStatus = 1
                led.value(ledStatus)
            elif frame % 10 == 0 and ledStatus == 1:
                ledStatus = 0
                led.value(ledStatus)

            if frame > 300:
                frame = 0
                sens.check_cal()
                #sens.status()

        except OSError:
            led.value(0)
            first = True

            print(wifimgr.hostip + " Connecting...", end='')
            connected = False
            connect_attempt = 0
            while not connected:
                try:
                    connect_attempt += 1
                    s.close()
                    s = usocket.socket()
                    s.connect(addr)
                    connected = True
                    print(" Connected")
                except OSError:
                    print(".", end='')
                    if connect_attempt > 30 or wifimgr.hostip == '':
                        # can't connect to host - go back to config mode
                        s.close()
                        wlan.active(False)
                        led.value(1)
                        wifimgr.start()
                        led.value(0)
                        machine.reset()
                    time.sleep_ms(2000)
