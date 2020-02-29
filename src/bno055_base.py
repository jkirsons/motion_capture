# bno055_base.py Minimal MicroPython driver for Bosch BNO055 nine degree of
# freedom inertial measurement unit module with sensor fusion.

# The MIT License (MIT)
#
# Copyright (c) 2017 Radomir Dopieralski for Adafruit Industries.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This is a port of the Adafruit CircuitPython driver to MicroPython, with
# modified/enhanced functionality.

# Original Author: Radomir Dopieralski
# Ported to MicroPython and extended by Peter Hinch
# This port copyright (c) Peter Hinch 2019

import utime as time
import ustruct
from micropython import const


_CHIP_ID = const(0xa0)

_CONFIG_MODE = const(0)
_NDOF_MODE = const(0x0c)
_NDOF_FMC_OFF_MODE = const(0x0b)

_POWER_NORMAL = const(0x00)
_POWER_LOW = const(0x01)
_POWER_SUSPEND = const(0x02)

_MODE_REGISTER = const(0x3d)
_PAGE_REGISTER = const(0x07)
_CALIBRATION_REGISTER = const(0x35)
_TRIGGER_REGISTER = const(0x3f)
_POWER_REGISTER = const(0x3e)
_ID_REGISTER = const(0x00)

_SYS_CLK_STATUS = const(0x38)
_SYS_STATUS = const(0x39)
_SYS_ERR = const(0x3A)
_SELFTEST_RESULT = const(0x36)
PROFILE_START = const(0x55)
PROFILE_END = const(0x6A)

class BNO055_BASE:

    def status(self):
        print("sys status: " + str(self._read(_SYS_STATUS)))
        print("sys err: " + str(self._read(_SYS_ERR)))
        print("self test: " + str(self._read(_SELFTEST_RESULT)))

    def __init__(self, i2c=None, address=0x28, crystal=True, transpose=(0, 1, 2), sign=(0, 0, 0), serial=None, calibration=None):
        if i2c is not None:
            self._i2c = i2c
        else:
            self._serial = serial
            self._i2c = None
        self.address = address
        self.crystal = crystal
        self.calibration = calibration
        self.mag = lambda: self.scaled_tuple(0x0e, 1/16)  # microteslas (x, y, z)
        self.accel = lambda: self.scaled_tuple(0x08, 1/100)  # m.s^-2
        self.lin_acc = lambda: self.scaled_tuple(0x28, 1/100)  # m.s^-2
        self.gravity = lambda: self.scaled_tuple(0x2e, 1/100)  # m.s^-2
        self.gyro = lambda: self.scaled_tuple(0x14, 1/16)  # deg.s^-1
        self.euler = lambda: self.scaled_tuple(0x1a, 1/16)  # degrees (heading, roll, pitch)
        self.quaternion = lambda: self.scaled_tuple(0x20, 1/(1 << 14), bytearray(8), '<hhhh')  # (w, x, y, z) - little endian, 4 shorts
        try:
            chip_id = self._read(_ID_REGISTER)
        except OSError:
            raise RuntimeError('No BNO055 chip detected.')
        if chip_id != _CHIP_ID:
            raise RuntimeError("bad chip id (%x != %x)" % (chip_id, _CHIP_ID))
        self.reset()


    def reset(self):
        self.mode(_CONFIG_MODE)
        try:
            self._write(_TRIGGER_REGISTER, 0x20)
        except OSError:  # error due to the chip resetting
            pass
        # wait for the chip to reset (650 ms typ.)
        time.sleep_ms(700)
        self._write(_POWER_REGISTER, _POWER_NORMAL)
        self._write(_PAGE_REGISTER, 0x00)
        if self.calibration is not None:
            self.write_calibration(self.calibration)
        self._write(_TRIGGER_REGISTER, 0x80 if self.crystal else 0)
        # Crystal osc seems to take time to start.
        time.sleep_ms(500 if self.crystal else 10)
        if hasattr(self, 'orient'):
            self.orient()  # Subclass
        self.mode(_NDOF_MODE)
        time.sleep_ms(50)

    def write_calibration(self, value):
        if len(value) == 0 or max(value) == 0:
            print("no calibration data")
            return
        time.sleep_ms(25)
        address = PROFILE_START
        while address <= PROFILE_END:
            self._write(address, value[address - PROFILE_START])
            address += 1
        print("Wrote calibration:")
        print(value)
        time.sleep_ms(10)

    def scaled_tuple(self, addr, scale, buf=bytearray(6), fmt='<hhh'):
        return tuple(b*scale for b in ustruct.unpack(fmt, self._readn(buf, addr)))

    def raw_quaternion(self):
        return self._readn(bytearray(8), 0x20)

    def raw_gravity(self):
        return self._readn(bytearray(6), 0x2e)

    def scale_tuple(self, scale, buf=bytearray(6), fmt='<hhh'):
        return tuple(b*scale for b in ustruct.unpack(fmt, buf))

    def temperature(self):
        t = self._read(0x34)  # Celcius signed (corrected from Adafruit)
        return t if t < 128 else t - 256

    # Return bytearray [sys, gyro, accel, mag] calibration data.
    def cal_status(self, s=bytearray(4)):
        cdata = self._read(_CALIBRATION_REGISTER)
        s[0] = (cdata >> 6) & 0x03  # sys
        s[1] = (cdata >> 4) & 0x03  # gyro
        s[2] = (cdata >> 2) & 0x03  # accel
        s[3] = cdata & 0x03  # mag
        return s

    def calibrated(self):
        s = self.cal_status()
        # https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/device-calibration
        return min(s[1:]) == 3 and s[0] > 0

# I2C ------------------
    # read byte from register, return int
    # memaddr = memory location within the I2C device
    def _read_i2c(self, memaddr, buf=bytearray(1)):
        self._i2c.readfrom_mem_into(self.address, memaddr, buf)
        return buf[0]

    # write byte to register
    def _write_i2c(self, memaddr, data, buf=bytearray(1)):
        buf[0] = data
        self._i2c.writeto_mem(self.address, memaddr, buf)

    # read n bytes, return buffer
    def _readn_i2c(self, buf, memaddr):  # memaddr = memory location within the I2C device
        self._i2c.readfrom_mem_into(self.address, memaddr, buf)
        return buf
# UART -----------------
# https://github.com/adafruit/Adafruit_Python_BNO055/blob/master/Adafruit_BNO055/BNO055.py

    # read byte from register, return int
    def _read_uart(self, memaddr, buf=bytearray(1)):
        buf = self._readn_uart(buf, memaddr)[0]
        return buf

    # write byte to register
    def _write_uart(self, memaddr, data, buf=bytearray(1)):
        # Build and send serial register write command.
        command = bytearray(5)
        command[0] = 0xAA  # Start byte
        command[1] = 0x00  # Write
        command[2] = memaddr# & 0xFF
        command[3] = 1     # Length (1 byte)
        command[4] = data #/& 0xFF 
        self._serial.write(command)
        # Read acknowledgement response (2 bytes).
        resp = bytearray(self._serial.read(2))
        # Verify register write succeeded if there was an acknowledgement.
        if resp[0] != 0xEE and resp[1] != 0x01:
            raise RuntimeError('Register write error: 0x{0}'.format(resp))

    # read n bytes, return buffer
    def _readn_uart(self, buf, memaddr):  # memaddr = memory location within the I2C device
        # Build and send serial register read command.
        command = bytearray(4)
        command[0] = 0xAA  # Start byte
        command[1] = 0x01  # Read
        command[2] = memaddr #& 0xFF
        command[3] = len(buf) #& 0xFF

        tries = 0
        while  True:
            self._serial.write(command)
            # Read acknowledgement response (2 bytes).
            resp = bytearray(self._serial.read(2))
            if resp is not None and len(resp) == 2 and not (resp[0] == 0xEE and resp[1] == 0x07):
                break
            print("UART retry...")
            tries += 1
            if tries == 5:
                raise RuntimeError('Register read error: 0x{0}'.format(resp))

        # Verify register read succeeded.
        if resp[0] != 0xBB:
            raise RuntimeError('Register read error: 0x{0}'.format(resp))
        # Read the returned bytes.
        length = resp[1]
        self._serial.readinto(buf, length)
        # logger.debug('Received: 0x{0}'.format(resp))
        if buf is None or len(buf) != length:
            raise RuntimeError('Timeout waiting to read data, is the BNO055 connected?')
        return buf

# Master ---------------
    # read byte from register, return int
    def _read(self, memaddr, buf=bytearray(1)):  # memaddr = memory location within the I2C device
        if self._i2c is not None:
            buf[0] = self._read_i2c(memaddr)
        else:
            buf[0] = self._read_uart(memaddr)
        return buf[0]

    # write byte to register
    def _write(self, memaddr, data, buf=bytearray(1)):
        if self._i2c is not None:
            self._write_i2c(memaddr, data, buf)
        else:
            self._write_uart(memaddr, data, buf)

    # read n bytes, return buffer
    def _readn(self, buf, memaddr):  # memaddr = memory location within the I2C device
        if self._i2c is not None:
            self._readn_i2c(buf, memaddr)
        else:
            self._readn_uart(buf, memaddr)
        return buf
# ---------------

    def mode(self, new_mode=None):
        old_mode = self._read(_MODE_REGISTER)
        if new_mode is not None:
            # This is empirically necessary if the mode is to be changed
            self._write(_MODE_REGISTER, _CONFIG_MODE)
            time.sleep_ms(20)  # Datasheet table 3.6
            if new_mode != _CONFIG_MODE:
                self._write(_MODE_REGISTER, new_mode)
                time.sleep_ms(10)  # Table 3.6
        return old_mode

    def external_crystal(self):
        return bool(self._read(_TRIGGER_REGISTER) & 0x80)
