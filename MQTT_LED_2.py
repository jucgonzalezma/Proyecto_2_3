#Script que enciende y apaga un LED desde la plataforma Adafruit IO
#!/bin/python3
import RPi.GPIO as GPIO
import time
import sys
from Adafruit_IO import RequestError, Client, Feed, MQTTClient
import Mykey

ADAFRUIT_IO_USERNAME = Mykey.user()
ADAFRUIT_IO_KEY = Mykey.llave()
FEED_ID = 'onoff'
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22, GPIO.OUT)

def connected(client):
    print ('Conectado a Adafruit IO! Escuchando cambios en {0}...'.format(FEED_ID))
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    print ('Suscrito a {0} con un Qos de {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    print ('Desconectado de Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print ('Feed {0} recibió un nuevo valor: {1}'.format(feed_id, payload))
    comando = int('{0}'.format(payload))
    if (comando == 0):
        print ("Led apagado")
        GPIO.output(22, GPIO.LOW)
    if (comando == 1):
        print ("Led Encendido")
        GPIO.output(22, GPIO.HIGH)

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

client.connect()

client.loop_blocking()
