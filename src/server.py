# Released under the MIT licence.
import utime
import machine
import network

import usocket
from sensors import sensors

def run():
    machine.freq(160000000)
    print('Machine ID: ' + str(machine.unique_id()))
    print('CPU Speed: ' + str(machine.freq()))
    print("Starting WiFi")

    led = machine.Pin(2, machine.Pin.OUT)

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    print("Connecting WiFi")
    sta_if.connect("Tomato24", "Stephen123")
    while not sta_if.isconnected():
        utime.sleep(1)
    print(sta_if.ifconfig())

    s = usocket.socket()
    addr = usocket.getaddrinfo('192.168.1.112', 61111, 0, usocket.SOCK_STREAM)[0][-1]

    sens = sensors([27, 25, 17, 16])
    sens.scan()

    led.value(1)
    utime.sleep_ms(500)
    led.value(0)
    frame = 0

    while True:
        utime.sleep_ms(5)
        sens.read_data()

        try:
            for data in sens.data_list:
                s.send(data)

            frame += 1
            if frame > 300:
                frame = 0
                sens.check_cal()
                for data in sens.data_list:
                    print(data)
                #sens.status()

        except OSError:
            s.close()
            s = usocket.socket()
            print("Connecting...", end='')
            connected = False
            connect_attempt = 0
            while not connected:
                try:
                    connect_attempt += 1
                    s.connect(addr)
                    connected = True
                    print(" Connected")
                except OSError:
                    print(".", end='')
                    if connect_attempt > 5:
                        machine.reset()
                    utime.sleep_ms(2000)
