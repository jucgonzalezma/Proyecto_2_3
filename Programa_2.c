//Script que enciende y apaga un LED conectado en la salida 2 de la Raspberry
#include <wiringPi.h>
#include <stdio.h>

int main(void){
 wiringPiSetup();
 pinMode(2, OUTPUT);
 while(1){
 digitalWrite(2, HIGH);
 delay(85);
 digitalWrite(2, LOW);
 delay(85);
}
}
