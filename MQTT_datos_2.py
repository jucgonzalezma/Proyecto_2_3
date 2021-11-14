#Script que publica el promedio de los valores sensados por el acelerometro ADXL345
#y por la sonda DS18B20 y los publica cada minuto en Adafruit IO
#!/bin/python3
import threading
import sys
import time
import random
import smbus
from w1thermsensor import W1ThermSensor, SensorNotReadyError
from Adafruit_IO import RequestError, Client, Feed, MQTTClient
import Mykey

ADAFRUIT_IO_USERNAME = Mykey.user()
ADAFRUIT_IO_KEY = Mykey.llave()
IO_FEED = 'temperatura'
IO_FEED_2 = 'acelerometro_x'
IO_FEED_3 = 'acelerometro_y'
IO_FEED_4 = 'acelerometro_z'

#Definimos variables globales
dato_temp = []
prom_temp = []
dato_x = []
dato_y = []
dato_z = []

N = 30    #Para configurar la resolución de tiempo de temperatura
M = 60    #Para configurar la resolución de tiempo del acelerometro

#Configuración sensor de temperatura
sensor = W1ThermSensor()

#Configuración acelerometro
bus = smbus.SMBus(1)
bus.write_byte_data(0x53, 0x2C, 0x0A)
value = bus.read_byte_data(0x53, 0x31)
value &= ~0x0F;
value |= 0x0B;
value |= 0x08;
bus.write_byte_data(0x53, 0x31, value)
bus.write_byte_data(0x53, 0x2D, 0x08)

def temperatura():
    while True:
        try:
            temperatura = sensor.get_temperature()
            dato_temp.append(temperatura)
            time.sleep(1)
        except SensorNotReadyError:
                if (len(prom_temp) > 0):
                    z = prom_temp.pop()
                    prom_temp.append(z) #En caso de falla en la lectura se duplica el ultimo valor sensado
                    prom_temp.append(z)
                    time.sleep(1)
                    print ('Error de lectura sensor de temperatura, se repite el último valor')

def acelerometro():
    while True:
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

        dato_x.append(x)
        dato_y.append(y)
        dato_z.append(z)
        time.sleep(1)

def publish():
    prom_x = []
    prom_y = []
    prom_z = []
    while True:
        if (len(dato_temp) > 0):
            prom_temp.append(dato_temp.pop(0))
        if (len(dato_x) > 0):
            prom_x.append(dato_x.pop(0))
        if (len(dato_y) > 0):
            prom_y.append(dato_y.pop(0))
        if (len(dato_z) > 0):
            prom_z.append(dato_z.pop(0))

        if (len(prom_temp) >= N):
            mean_temp = round(sum(prom_temp)/len(prom_temp), 2)
            print ('Publicando {0} en {1}.'.format(mean_temp, IO_FEED))
            client.publish(IO_FEED, mean_temp)
            prom_temp.clear()
            dato_temp.clear()

        if (len(prom_x) == M):
            mean_x = round(sum(prom_x)/len(prom_x), 3)
            print ('Publicando {0} en {1}.'.format(mean_x, IO_FEED_2))
            client.publish(IO_FEED_2, mean_x)
            prom_x.clear()
            dato_x.clear()
        if (len(prom_y) == M):
            mean_y = round(sum(prom_y)/len(prom_y), 3)
            print ('Publicando {0} en {1}.'.format(mean_y, IO_FEED_3))
            client.publish(IO_FEED_3, mean_y)
            prom_y.clear()
            dato_y.clear()
        if (len(prom_z) == M):
            mean_z = round(sum(prom_z)/len(prom_z), 3)
            print ('Publicando {0} en {1}.'.format(mean_z, IO_FEED_4))
            client.publish(IO_FEED_4, mean_z)
            prom_z.clear()
            dato_z.clear()

def connected(client):
    print ('Conectado a Adafruit IO! Publicando a {0}, {1}, {2}, {3}...'.format(IO_FEED, IO_FEED_2, IO_FEED_3, IO_FEED_4))
    client.subscribe(IO_FEED)
    client.subscribe(IO_FEED_2)
    client.subscribe(IO_FEED_3)
    client.subscribe(IO_FEED_4)

def disconnected(client):
    print ('Desconectado de Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print ('Feed {0} recibió un nuevo valor: {1}'.format(feed_id, payload))

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

client.connect()

client.loop_background()

print ('Publicando un nuevo mensaje cada minuto (presiona Ctrl+C para salir)...')

tt=threading.Thread(target=temperatura)
tt2=threading.Thread(target=acelerometro)
tt3=threading.Thread(target=publish)
tt.start()
tt2.start()
tt3.start()
