
import os, machine
import esp
from bno055 import *
#import time

class sensors:
    profile_length = const(0x6A - 0x55 + 1)
    profile = [[bytearray(profile_length) for x in range(2)] for y in range(2)]
    stored_profile = [[bytearray(profile_length) for x in range(2)] for y in range(2)]
    profile_cal_status = [[bytearray(4) for x in range(2)] for y in range(2)]
    addr_start = esp.flash_user_start()

    data_list = []
    cal_status = [[bytearray(4) for x in range(2)] for y in range(2)]
    not_cal_count = [[0 for x in range(2)] for y in range(2)]
    data = [[bytearray(11) for x in range(2)] for y in range(2)]
    found = []
    imus = []
    connected_imus = 0

    def __init__(self, pins):
        self.i2c = []
        print("Starting Sensors")
        self.i2c.append(machine.I2C(0, scl=machine.Pin(pins[0]), sda=machine.Pin(pins[1]), freq=400000))
        self.i2c.append(machine.I2C(1, scl=machine.Pin(pins[2]), sda=machine.Pin(pins[3]), freq=400000))
        self.read_config_file()

    def read_config_file(self):
        try:
            file = open(file="cal.txt", mode="rb")
        except OSError:
            file = open(file="cal.txt", mode="w")
            file.close()
            file = open(file="cal.txt", mode="rb")
        #file.seek(0)
        for i in range(2):
            for j in range(2):
                file.readinto(self.stored_profile[i][j], self.profile_length)
                print(self.stored_profile[i][j])
        for i in range(2):
            for j in range(2):
                file.readinto(self.profile_cal_status[i][j], len(self.profile_cal_status[i][j]))
                print(self.profile_cal_status[i][j])
        file.close()

    def write_config_file(self):
        file = open(file="cal.txt", mode="wb+")
        #self.file.seek(0)
        for i in range(2):
            for j in range(2):
                file.write(self.stored_profile[i][j])
                print(self.stored_profile[i][j])
        for i in range(2):
            for j in range(2):
                file.write(self.profile_cal_status[i][j])
                print(self.profile_cal_status[i][j])
        file.close()

    def is_found(self, bus_list):
        ret = []
        ret.append(1 if 0x28 in bus_list else 0)
        ret.append(1 if 0x29 in bus_list else 0)
        if 0x28 in bus_list:
            self.connected_imus += 1
        if 0x29 in bus_list:
            self.connected_imus += 1
        return ret

    def scan(self):
        self.connected_imus = 0
        self.found = []
        self.found.append(self.is_found(self.i2c[0].scan()))
        self.found.append(self.is_found(self.i2c[1].scan()))
        print('Devices found: ', end='')
        print(self.found)

        self.imus = []
        for i in range(2):
            imu_bus = []
            for j in range(2):
                if self.found[i][j]:
                    imu_bus.append(BNO055(i2c=self.i2c[i], address=0x28 if j == 0 else 0x29, calibration=self.stored_profile[i][j]))
                else:
                    imu_bus.append(None)
            self.imus.append(imu_bus)

    def reconnect(self, i, j):
        try:
            #if not self.imus[i][j] is None:
            #    del self.imus[i][j]
            print('Reset ['+str(i)+'],['+str(j)+']', end='')
            self.imus[i][j].reset()
        except RuntimeError:
            pass
        except OSError:
            pass

    def read_data(self):
        self.data_list.clear()
        for j in range(2):
            for i in range(2):
                if self.found[i][j]:
                    try:
                        self.data[i][j][0] = 0 # Transaction Type
                        self.data[i][j][1] = i # Bus Number
                        self.data[i][j][2] = j # Device Number
                        self.data[i][j][3:11] = self.imus[i][j].raw_quaternion()
                        #self.data[i][j][11:17] = self.imus[i][j].raw_gravity()
                        self.data_list.append(self.data[i][j])
                        #time.sleep_ms(1)
                    except OSError:
                        print('X ['+str(i)+'],['+str(j)+']', end='')
                        self.reconnect(i, j)
                        continue

    def read_grav(self):
        self.data_list.clear()
        for j in range(2):
            for i in range(2):
                if self.found[i][j]:
                    try:
                        self.data[i][j][0] = 1 # Transaction Type
                        self.data[i][j][1] = i # Bus Number
                        self.data[i][j][2] = j # Device Number
                        self.data[i][j][3:9] = self.imus[i][j].raw_gravity()
                        self.data_list.append(self.data[i][j])
                    except OSError:
                        print('X ['+str(i)+'],['+str(j)+']', end='')
                        self.reconnect(i, j)
                        continue

    def read_id(self):
        self.data_list.clear()
        machine_id = machine.unique_id()
        self.data[0][0][0] = 9 # Transaction Type
        self.data[0][0][1:11] = machine_id
        self.data_list.append(self.data[0][0])

    def read_cal(self):
        for j in range(2):
            for i in range(2):
                if self.found[i][j]:
                    try:
                        self.cal_status[i][j] = self.imus[i][j].cal_status(self.cal_status[i][j])
                    except OSError:
                        print("Error reading calibration status")

    def check_cal(self):
        self.read_cal()
        changed = False
        for j in range(2):
            for i in range(2):
                if self.found[i][j]:
                    cal = self.cal_status[i][j]
                    print("Cal: sys: "+str(cal[0])+" gyro: "+str(cal[1])+" acc: "+str(cal[2])+" mag: "+str(cal[3]), end="")

                    higher = 0
                    lower = 0
                    for k in range(len(self.profile_cal_status[i][j])):
                        if self.cal_status[i][j][k] > self.profile_cal_status[i][j][k]:
                            higher += 1
                        if self.cal_status[i][j][k] < self.profile_cal_status[i][j][k]:
                            lower += 1
                        #print(str(self.cal_status[i][j]) + " vs " + str(self.profile_cal_status[i][j]))
                    print(" Higher: " + str(higher) + " Lower: " + str(lower))
                    if (higher > 0 and lower == 0):
                        self.profile[i][j] = self.imus[i][j].read_profile(self.profile[i][j])
                        for k in range(len(self.cal_status[i][j])):
                            self.profile_cal_status[i][j][k] = self.cal_status[i][j][k]
                        for k in range(len(self.profile[i][j])):
                            self.stored_profile[i][j][k] = self.profile[i][j][k]
                        changed = True
        if changed:
            print("Saving File")
            self.write_config_file()


# UART connection
#ser = machine.UART(2, baudrate=115200, bits=8, parity=None, stop=1, tx=17, rx=16, timeout=100)
#imu = BNO055(serial=ser)

#    print('Temperature {}°C'.format(imu.temperature()))
#    print('Mag       x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.mag()))
#    print('Gyro      x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.gyro()))
#    print('Accel     x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.accel()))
#    print('Lin acc.  x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.lin_acc()))
#    print('Gravity   x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.gravity()))
#euler = imu.euler()
