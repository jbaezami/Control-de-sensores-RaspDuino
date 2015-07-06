#include <SFE_BMP180.h>
#include <Wire.h>
#include <SoftwareSerial.h>
#define DHT21_PIN 14      // ADC0
#define ALTITUDE 459.0 //default altitude CACERES

SFE_BMP180 sensor_bmp;

// serial Bd
int serialValue = 9600;

// recepcion de datos
int incomingByte = 0;
int decimalPoint = 3;
float decimales = 0.0;

// calibracion
float callibration = 0.0;
float calibracionAlcohol = 0.0, calibracionHumedad = 0.0, calibracionMetano = 0.0, 
      calibracionPresion = 0.0, calibracionTemperatura = 0.0;
bool calibrando = false;
bool bmpProblem = false;

int posByte = 1000;
int signo = 1;
int sensorMetanoPin = A1; //the AOUT pin of the metano sensor goes into analog pin A1 of the arduino
int led = 11; //led rojo
int ledV = 10; //led verde
int buzzer = 12;

float temp1, temp2, temperature, humidity, baresAbs, mercuryAbs, baresRel, mercuryRel, altitudeMeters;
int metano, limiteAlcohol, alcohol;
byte dht21_dat[5];

const int alcoholAnalogicPin=2;//the AOUT pin of the alcohol sensor goes into analog pin A0 of the arduino
const int alcoholDigitalPin=8;//the DOUT pin of the alcohol sensor goes into digital pin D8 of the arduino

// Alerta
bool alertando = false;
bool sonar = false;
int vueltaAlerta = 100;

void mandarAlcohol()
{
  if (alcohol < 300)
    Serial.println("A0A");
  else
    Serial.println("A1A");
  Serial.flush();
}

void mandarHumedad()
{
  String percent = "H", zero = "0", hum = "";
  if (humidity < 10){
    hum = percent + zero + humidity + percent;
  }
  else
    hum = percent + humidity + percent;
  Serial.println(hum);
  Serial.flush();
}

void mandarMetano()
{
  if (metano < 80)
    Serial.println("M0M");
  else
    Serial.println("M1M");
  Serial.flush();
}

void mandarPresion()
{
  String percent = "P", zero = "0", pres = "";
  if (baresRel < 1000){
    pres = percent + zero + baresRel + percent;
  }
  else if (baresRel < 100){
    pres = percent + zero + zero + baresRel + percent;
  }
  else if (baresRel < 10){
    pres = percent + zero + zero + zero + baresRel + percent;
  }
  else
    pres = percent + baresRel + percent;
  Serial.println(pres);
  Serial.flush();
}

void mandarTemperatura()
{
  String percent = "T", zero = "0", temp = "";
 // thermistorReading = thermistorReading + callibration;
  temperature = (temp1 + temp2) / 2;
  if (temperature < 10){
    temp = percent + zero + temperature + percent;
  }
  else
    temp = percent + temperature + percent;
  Serial.println(temp);
  Serial.flush();
}

String formatearAlcohol()
{
  if (alcohol < 300)
    return "A0A";
  else
    return "A1A";
}

String formatearHumedad()
{
  String percent = "H", zero = "0", hum = "";
  if (humidity < 10){
    hum = percent + zero + humidity + percent;
  }
  else
    hum = percent + humidity + percent;
  return hum;
}

String formatearMetano()
{
  if (metano < 80)
    return "M0M";
  else
    return "M1M";
}

String formatearPresion()
{
  String percent = "P", zero = "0", pres = "";
  if (baresRel < 1000){
    pres = percent + zero + baresRel + percent;
  }
  else if (baresRel < 100){
    pres = percent + zero + zero + baresRel + percent;
  }
  else if (baresRel < 10){
    pres = percent + zero + zero + zero + baresRel + percent;
  }
  else
    pres = percent + baresRel + percent;
  return pres;
}

String formatearTemperatura()
{
  String percent = "T", zero = "0", temp = "";
 // thermistorReading = thermistorReading + callibration;
  temperature = (temp1 + temp2) / 2;
  if (temperature < 10){
    temp = percent + zero + temperature + percent;
  }
  else
    temp = percent + temperature + percent;
  return temp;
}

byte read_dht21_dat()
{
  byte i = 0;
  byte result=0;
  for(i=0; i< 8; i++){
    while(!digitalRead(DHT21_PIN));  // wait for 50us
    delayMicroseconds(30);
    if(digitalRead(DHT21_PIN))
      result |=(1<<(7-i));
    while(digitalRead(DHT21_PIN));  // wait '1' finish
  }
  return result;
}

void calcularDHT()
{
  byte dht21_dat[5];
  byte dht21_in;
  byte i;
  // start condition
  // 1. pull-down i/o pin from 18ms
  digitalWrite(DHT21_PIN,LOW);
  delay(18);
  digitalWrite(DHT21_PIN,HIGH);
  delayMicroseconds(40);
  pinMode(DHT21_PIN,INPUT);
  while(digitalRead(DHT21_PIN)){}
  delayMicroseconds(80);
  while(!digitalRead(DHT21_PIN)){}
  delayMicroseconds(80);
  // now ready for data reception
  for (i=0; i<5; i++)
    dht21_dat[i] = read_dht21_dat();
  pinMode(DHT21_PIN,OUTPUT);
  digitalWrite(DHT21_PIN,HIGH);
  byte dht21_check_sum = dht21_dat[0]+dht21_dat[1]+dht21_dat[2]+dht21_dat[3];
  // check check_sum
  if(dht21_dat[4]!= dht21_check_sum){}
  else{
    humidity=((float)(dht21_dat[0]*256+dht21_dat[1]))/10;
    temp1=((float)(dht21_dat[2]*256+dht21_dat[3]))/10;
  }
}

void calcularTemperatura()
{
  char status;
  double T;  
  status = sensor_bmp.startTemperature();
  if (status != 0)
  {
    // Wait for the measurement to complete:
    delay(status);

    // Retrieve the completed temperature measurement:
    // Note that the measurement is stored in the variable T.
    // Function returns 1 if successful, 0 if failure.

    status = sensor_bmp.getTemperature(T);
    if (status != 0)
    {
      temp2 = T;
     }
    else 
      bmpProblem = true;
  }
  else
    bmpProblem = true;
}

void calcularMetano()
{  
  metano = analogRead(sensorMetanoPin);
}

void calcularPresion()
{
  char status;
  double T,P,p0,a;
  
  status = sensor_bmp.startsensor_bmp(3);
  if (status != 0)
  {
    // Wait for the measurement to complete:
    delay(status);
    status = sensor_bmp.getsensor_bmp(P,T);
    if (status != 0)
    {
      baresAbs = P;
      mercuryAbs = P*0.0295333727;
      p0 = sensor_bmp.sealevel(P,ALTITUDE);
      baresRel = p0;
      mercuryRel = p0*0.0295333727;
      a = sensor_bmp.altitude(P,p0);
      altitudeMeters = a;
    }
    else 
      bmpProblem = true;
  }
  else
    bmpProblem = true;
}

void calcularAlcohol()
{
  alcohol= analogRead(alcoholAnalogicPin);
  limiteAlcohol= digitalRead(alcoholDigitalPin);
}

void recibirCalibrado()
{
  if (posByte > 100){
    callibration = 0;
    posByte = posByte/10;
    switch(incomingByte){
      case 43:
        signo = 1;
        break;
      case 45:
        signo = -1;
        break;
    }
  }
  else if (posByte > 1){
    callibration = callibration + (incomingByte-48)*posByte;
    posByte = posByte/10;
    decimalPoint = 3;
  }
  else{
    if (decimalPoint == 3){
      callibration = (callibration + incomingByte-48);
      decimalPoint--;
    }
    else if (decimalPoint == 2)
      decimalPoint--;
    else if (decimalPoint == 1){
      decimales = (incomingByte-48)*10;
      decimalPoint--;
    }
    else if (decimalPoint == 0){
      decimales = decimales + (incomingByte-48);
      decimalPoint--;
      callibration = (callibration + (decimales/100))*signo;
    }
    else{
//      Serial.print(incomingByte);
//      Serial.print(" - ");
//      Serial.println(callibration);
      asignarCalibracion(incomingByte, callibration);
      calibrando = false;
      posByte = 1000;
    }
  }
}

void alertar(){
  sonar = !sonar;
  if (sonar)
    digitalWrite(buzzer, HIGH);
  else
    digitalWrite(buzzer, LOW);
  vueltaAlerta--;
  if (vueltaAlerta == 0){
    digitalWrite(buzzer, LOW);
    alertando = false;
    vueltaAlerta = 100;
  }
}

void mostrarValores()
{ 
  Serial.println("---------------------------------------------------------");
  Serial.println("------------------------ VALORES ------------------------");
  Serial.println("---------------------------------------------------------");
  Serial.print("T1: ");                 Serial.print(temp1);
  Serial.print("  T2: ");               Serial.println(temp2);
  Serial.print("Humedad: ");            Serial.println(humidity);
  Serial.print("Presion bares ABS: ");  Serial.print(baresAbs);
  Serial.print("  Presion merc ABS ");    Serial.println(mercuryAbs);
  Serial.print("Presion bares REL: ");  Serial.print(baresRel);
  Serial.print("  Presion merc REL: ");   Serial.println(mercuryRel);
  Serial.print("Altura metros: ");      Serial.println(altitudeMeters);
  Serial.print("Metano: ");             Serial.println(metano);
  Serial.print("Limite alcohol: ");     Serial.print(limiteAlcohol);
  Serial.print("  Alcohol: ");            Serial.println(alcohol);
  Serial.println("---------------------------------------------------------");
}

void asignarCalibracion(int opcion, float calibracion)
{
  switch (opcion){
    case 65: // A
      calibracionAlcohol = calibracion;
      break; 
    case 97: // a
      calibracionAlcohol = calibracion;
      break;
    case 72: // H
      calibracionHumedad = calibracion;
      break; 
    case 104: // h
      calibracionHumedad = calibracion;
      break;
    case 77: // M
      calibracionMetano = calibracion;
      break; 
    case 109: // m
      calibracionMetano = calibracion;
      break;
    case 80: // P
      calibracionPresion = calibracion;
      break; 
    case 112: // p
      calibracionPresion = calibracion;
      break;
    case 84: // T
      calibracionTemperatura = calibracion;
      break;
    case 116: // t
      calibracionTemperatura = calibracion;
      break;
    default:
      Serial.println("Error");    
  }
}

void setup()
{
  pinMode(DHT21_PIN,OUTPUT);
  pinMode(alcoholDigitalPin, INPUT);
  pinMode(led, OUTPUT);
  pinMode(ledV, OUTPUT);
  digitalWrite(ledV, HIGH);
  pinMode(buzzer, OUTPUT);
  Serial.begin(serialValue);
  //if (!sensor_bmp.begin())
  //  Serial.println("ERROR EN SENSOR DE PRESION");
}

void loop()
{ 
  /*if (bmpProblem){
    Serial.println("Problema en medidor bmp");
    sensor_bmp.begin();
    bmpProblem = false;
  }*/
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();
    //Serial.print("I received: ");
    //Serial.println(incomingByte, DEC);
    if (!calibrando){
      switch (incomingByte){
        case 33: // !
          alertando = !alertando;
          if (!alertando){
            digitalWrite(buzzer, LOW);
            vueltaAlerta = 100;
          }
          break;
        case 36: // $
          Serial.println(formatearTemperatura()+formatearHumedad()+formatearPresion()+formatearAlcohol()+formatearMetano());
          Serial.flush();
          break;
        case 38: // &
          mostrarValores();
          break;
        case 65: // A
          mandarAlcohol();
          break; 
        case 97: // a
          mandarAlcohol();
          break;
        case 67: // C
          calibrando = true;
          break; 
        case 99: // c
          calibrando = true;
          break;
        case 72: // H
          mandarHumedad();
          break; 
        case 104: // h
          mandarHumedad();
          break;
        case 77: // M
          mandarMetano();
          break; 
        case 109: // m
          mandarMetano();
          break;
        case 80: // P
          mandarPresion();
          break; 
        case 112: // p
          mandarPresion();
          break;
        case 84: // T
          mandarTemperatura();
          break;
        case 116: // t
          mandarTemperatura();
          break;
        default:
          Serial.println("Error");    
      }
    }
    else{
      if ((incomingByte == 67)||(incomingByte == 99))
        calibrando = false;
      else
        recibirCalibrado();
    }
  }
  else{  
    /*calcularDHT();
    calcularTemperatura();
    calcularMetano();
    calcularPresion();
    calcularAlcohol();*/
    if ((metano > 80)||(alcohol > 300)){
      digitalWrite(led, HIGH);
      digitalWrite(ledV, LOW);
    }else{
      digitalWrite(led, LOW);
      digitalWrite(ledV, HIGH);
    }
    if (alertando)
      alertar();
    delay(1000);
  }
}
