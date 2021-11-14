//Script que enciende y apaga un LED conectado en la salida 0 de la Raspberry
#include <wiringPi.h>
#include <stdio.h>

int main(void){
 wiringPiSetup();
 pinMode(0, OUTPUT);
 digitalWrite(0, HIGH);
 delay(20);
 digitalWrite(0, LOW);
 delay(20);
}

