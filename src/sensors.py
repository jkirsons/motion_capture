
import machine
from bno055 import *

class sensors:
    data_list = []
    data = []
    found = []
    imus = []

    def __init__(self, pins):
        self.i2c = []
        print("Starting Sensors")
        self.i2c.append(machine.I2C(0, scl=machine.Pin(pins[0]), sda=machine.Pin(pins[1])))
        self.i2c.append(machine.I2C(1, scl=machine.Pin(pins[2]), sda=machine.Pin(pins[3])))

    def scan(self):
        self.found = []
        self.found.append(self.i2c[0].scan())
        self.found.append(self.i2c[1].scan())
        print('Devices found: ', end='')
        print(self.found)

        self.imus = []
        for i in range(len(self.found)):
            imu_bus = []
            data_row = []
            for j in range(len(self.found[i])):
                try:
                    imu_bus.append(BNO055(i2c=self.i2c[i], address=self.found[i][j]))
                except OSError:
                    print("Error reading I2C")
                data_row.append(bytearray(11))
            self.data.append(data_row)
            self.imus.append(imu_bus)

    def read_data(self):
        self.data_list.clear()
        for (i, bus) in enumerate(self.imus):
            for (j, imu) in enumerate(bus):
                try:
                    self.data[i][j][0] = 0 # Transaction Type
                    self.data[i][j][1] = i # Bus Number
                    self.data[i][j][2] = self.found[i][j] # Device Number
                    self.data[i][j][3:11] = imu.raw_quaternion(self.data[i][j][3:11])
                    self.data_list.append(self.data[i][j])
                except OSError:
                    print('X', end='')
                    continue

# UART connection
#ser = machine.UART(2, baudrate=115200, bits=8, parity=None, stop=1, tx=17, rx=16, timeout=100)
#imu = BNO055(serial=ser)


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