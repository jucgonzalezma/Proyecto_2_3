#Script que lee los valores sensados por el acelerometro ADXL345
#!/bin/python3
import smbus
import time
from time import sleep
import sys

bus = smbus.SMBus(1)
bus.write_byte_data(0x53, 0x2C, 0x0A)
value = bus.read_byte_data(0x53, 0x31)
value &= ~0x0F;
value |= 0x0B;
value |= 0x08;
bus.write_byte_data(0x53, 0x31, value)
bus.write_byte_data(0x53, 0x2D, 0x08)

def getAxes():
    bytes = bus.read_i2c_block_data(0x53, 0x32, 6)
    x = bytes[0] | (bytes[1] << 8)
    if(x & (1 << 16 - 1)):
        x = x - (1<<16)
    y = bytes[2] | (bytes[3] << 8)
    if(y & (1 << 16 - 1)):
        y = y - (1<<16)
    z = bytes[4] | (bytes[5] << 8)
    if(z & (1 << 16 - 1)):
        z = z - (1<<16)

    x = x * 0.004*9.80665 
    y = y * 0.004*9.80665
    z = z * 0.004*9.80665

    x = round(x, 4)
    y = round(y, 4)
    z = round(z, 4)

    print("   x = %.4f ms2" %x)
    print("   y = %.4f ms2" %y)
    print("   z = %.4f ms2" %z)

try:
    while True:
        getAxes()
        time.sleep(1)
