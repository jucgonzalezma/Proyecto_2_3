#Script que mediante hilos lee los valores del acelerometro ADXL345
#Lee los valores de la sonda de temperatura DS18B20
#Saca el promedio de los valores definidos y los publica por serial
#!/bin/python3
import threading
import serial
import time
import smbus
import sys
import base64

#Valores globales
valor_N = []
ser = serial.Serial ('/dev/ttyAMA0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
dato_x = []
dato_y = []
dato_z = []

#Definen variables del sensor
bus = smbus.SMBus(1)
bus.write_byte_data(0x53, 0x2C, 0x0A)
value = bus.read_byte_data(0x53, 0x31)
value &= ~0x0F;
value |= 0x0B;
value |= 0x08;
bus.write_byte_data(0x53, 0x31, value)
bus.write_byte_data(0x53, 0x2D, 0x08)

def hilo_1():
    while True:
        bytes = bus.read_i2c_block_data(0x53, 0x32, 6)
        x = bytes[0] | (bytes[1] << 8)
        if (x & (1 << 16 -1)):
            x = x - (1<<16)
        y = bytes[2] | (bytes[3] << 8)
        if (y & (1 << 16 - 1)):
            y = y - (1<<16)
        z = bytes[4] | (bytes[5] << 8)
        if (z & (1 << 16 - 1)):
            z = z - (1<<16)
        x = x * 0.004 * 9.80665
        y = y * 0.004 * 9.80665
        z = z * 0.004 * 9.80665
        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)
        dato_x.append(x)
        dato_y.append(y)
        dato_z.append(z)
        time.sleep(0.5)

def hilo_2():
    N = 5
    prom_x = []
    prom_y = []
    prom_z = []
    print ("El valor inicial de N es:", N)
    while True:
        if (len(dato_x) > 0):
            prom_x.append(dato_x.pop(0))
        if (len(dato_y) > 0):
            prom_y.append(dato_y.pop(0))
        if (len(dato_z) > 0):
            prom_z.append(dato_z.pop(0))
        if (len(prom_x) == N):
            mean_x = round(sum(prom_x)/len(prom_x), 4)
            print (len(prom_x))

            prom_x.clear()
            dato_x.clear()
        if (len(prom_y) == N):
            mean_y = round(sum(prom_y)/len(prom_y), 4)
            print (len(prom_y))
            prom_y.clear()
            dato_y.clear()
        if (len(prom_z) == N):
            mean_z = round(sum(prom_z)/len(prom_z), 4)
            print (len(prom_z))
            prom_z.clear()
            dato_z.clear()
            if (len(valor_N) > 0):
                N = valor_N.pop(0)
                print ("El valor de N se modificó a:", N)
            xx = str(mean_x)
            yy = str(mean_y)
            zz = str(mean_z)
            tuple_data = (xx,yy,zz)
            send_data = ','.join(tuple_data)
            send_data += "\r\n"
            ser.write(send_data.encode())
        time.sleep(1)

def hilo_3():
    while True:
        received_data = ser.read()
        time.sleep(0.03)
        data_left = ser.inWaiting()
        received_data += ser.read(data_left)
        final_message = received_data.decode('ascii')
        split_message = final_message.split("-")
        if (split_message[0] == '##PROMEDIO' and len(split_message[1]) == 3 and split_message[1].isnumeric() == True and split_message[2] == '##\n' and int(split_message[1]) > 0):
            NNN = int(split_message[1])
            valor_N.append(NNN)
        else:
            string = "Trama incorrecta, debe ser ##PROMEDIO-NNN-##\n y NNN un numero > 0"
            print (repr(string))

tt=threading.Thread(target=hilo_1)
tt2=threading.Thread(target=hilo_2)
tt3=threading.Thread(target=hilo_3)
tt.start()
tt2.start()
tt3.start()
