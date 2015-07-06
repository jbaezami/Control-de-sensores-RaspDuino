#!/usr/bin/env python

#	Programa de registro de sensores raspberry
#	Desarrollado por: Juan Antonio Baeza Miralles
#	Encargado por: LARUEX
#	Proyecto: Trabajo fin de grado - Uso de maquinas de bajo coste en entornos agresivos con el hardware

#	Manual del programados:
#	Requerimientos:
#		- Base de datos formato sqlite3: para crear 'CREATE TABLE temps (timestamp DATETIME, tinterna NUMERIC, texterna NUMERIC);'
#		- Asegurar permisos de escritura sobre la base de datos
#		- Arduino conectado en el USB '/dev/ttyACM0'
#	Formatos:
#		- Escritura de registros en base de datos: 'python escribirTemperaturaCompleta.py'
#		- Configuracion de arduino:
#			* Calibracion del termometro: 'python escribirTemperaturaCompleta.py [ARGS]'
#				donde 
#					el 1 digito debe ser c o C e indica que la funcion a ejecutar es calibrado
#					el 2 digito debe ser + o - e indica si se debe sumar el valor o restar
#					el 3,4 y 5 digito (3 digitos obligatorios) es el valor en fahrenheit a sumar o restar para calibrar el sensor 


from serial import Serial
import re
import subprocess
import os
import sqlite3
import datetime
import sys
import pexpect
import time

# Configuracion
bd = 'templogCompleto.db'
serial_port = '/dev/ttyACM0'
serial_bauds = 9600
intentos = 3
f = open('log_temp', 'a')

avisoTempInterna = 0
avisoTempExterna = 0
avisoAlcohol = 0
avisoMetano = 0

texterna = 0.0
presion = 0.0
humedad = 0.0
alcohol = 0
metano = 0

def actualizar_alertas() :
	global avisoTempInterna, avisoTempExterna, avisoAlcohol, avisoMetano
	conn=sqlite3.connect(bd)
	curs=conn.cursor()
	curs.execute('SELECT valor FROM sensores WHERE sensor ="TINTERNA"')
	avisoTempInterna = str(curs.fetchone())[1]
        curs.execute('SELECT valor FROM sensores WHERE sensor ="TEXTERNA"')
        avisoTempEnterna = str(curs.fetchone())[1]
	curs.execute('SELECT valor FROM sensores WHERE sensor ="ALCOHOL"')
        avisoAlcohol = str(curs.fetchone())[1]
        curs.execute('SELECT valor FROM sensores WHERE sensor ="METANO"')
        avisoMetano = str(curs.fetchone())[1]
	conn.commit()
	conn.close()

def cambiar_alerta_sensor(sensor,valor):
	conn=sqlite3.connect(bd)
        curs=conn.cursor()
        sentence = 'UPDATE sensores SET valor = ' + str(valor) + ' WHERE sensor="' 
	sentence = sentence + sensor + '"'
	curs.execute(sentence)
        conn.commit()
        conn.close()

def enviar_aviso(sensor, valor):
	#print "Envio mensaje: "
	#print sensor
	contacto = "Baeza_Juan_Ant"                          #Contacto a quien va el mensaje
 	mensaje = "Alerta en workStation1 sensor: " + sensor 	#Mensaje a enviar
 	telegram = pexpect.spawn('/home/pi/tg/bin/telegram-cli -k /home/pi/tg/tg-server.pub -W') #Inicia Telegram
 	telegram.expect('0m')                            #Espera a que termine de iniciar
 	telegram.sendline('msg '+contacto+' '+mensaje)   #Ejecuta el comando msg
 	telegram.sendline('quit')                        #cierra Telegram
	
def open_serial_port() :
	try:
		s = Serial(serial_port, serial_bauds)
		return s
	except serial.serialutil.SerialException:
		f.write("Error al conectar ARDUINO\n")
		sys.exit("Error al conectar ARDUINO")

def config_arduino(c):
	s = open_serial_port()
	s.write(c)

def pedir_datos(): 
	global texterna, presion, humedad, alcohol, metano
	s = open_serial_port()
	s.write('$')
	f.write("He pedido T\n")
#	print "Pido T y espero\n"
	time.sleep(2)
	line = s.readline()
#	print "He leido T: "
#	print line
	time.sleep(2)
	f.write("Recibo T: ")
	f.write(line)
	if check_values(line) :
#		print "Check OK"
		texterna = float(line[1:6])
		humedad = float(line[8:13])
		presion = float(line[15:22])
		alcohol = int(line[24])
		metano = int(line[27])
		return True
	else :
		#print "Siguiente intento"
		return False

def check_values(s):
	# formato
	# T30.25T    H 3 3 . 3 0 H       P 0 9 4 6 . 7 6 P       A 0 A       M 0 M 
	# 0123456    7 8 9 10111213      141516171819202122      232425      262728
	if s[0]=='T' and s[6]=='T' and s[7]=='H' and s[13]=='H' and s[14]=='P' and s[22]=='P' and s[23]=='A' and s[25]=='A' and s[26]=='M' and s[28]=='M':
		return True
	else:
		return False

def check_alcohol(s):
	if s[0]=='A' and s[1].isdigit() and s[2]=='A' :
		return True
	else :
#			f.write("Valor erroneo\n")
		return False

def check_metano(s):
	if s[0]=='M' and s[1].isdigit() and s[2]=='M' :
		return True
	else :
#			f.write("Valor erroneo\n")
		return False
						
def check_value_temp(s):
	if (s[0]=='T' and s[1].isdigit() and s[2].isdigit() and (s[3] == '.') and s[4].isdigit() and s[6]=='T') :
		return True
	else :
		f.write("Valor erroneo\n")
		return False

def check_value_hum(s):
	if (s[0]=='H' and s[1].isdigit() and s[2].isdigit() and (s[3] == '.') and s[4].isdigit() and s[0]=='H') :
		return True
	else :
		f.write("Valor erroneo\n")
		return False

def check_value_pres(s):
	if (s[0]=='P' and s[1].isdigit() and s[2].isdigit() and s[3].isdigit() 
	and s[4].isdigit() and (s[5] == '.') and s[6].isdigit() and s[8]=='P') :
		return True
	else :
		f.write("Valor erroneo\n")
		return False
				
def read_temp_arduino():
	global intentos
	s = open_serial_port()
        intentos = 3
	while intentos > 0:
		s.write('T')
		f.write("He pedido T\n")
		time.sleep(1)
		line = s.readline()
		f.write("Temperatura externa: ")
		f.write(line)
		if check_value_temp(line) :
			intentos = -1
		else :
			#print "Siguiente intento"
			intentos = intentos - 1
	return line[1:5] #cambiar a line[1:6] para coger 2 decimales
	
def read_hum_arduino():
	global intentos
	s = open_serial_port()
	intentos = 3
	while intentos > 0:
		s.write('H')
                f.write("He pedido H\n")
                time.sleep(1)
		line = s.readline()
		f.write("Humedad: ")
		f.write(line)
		if check_value_hum(line) :
			intentos = -1
		else :
			#print "Siguiente intento"
			intentos = intentos - 1
	return line[1:5] #cambiar a line[1:6] para coger 2 decimales

def read_metano_arduino():
	global intentos
	s = open_serial_port()
        intentos = 3
	while intentos > 0:
		s.write('M')
                f.write("He pedido M\n")
                time.sleep(1)
		line = s.readline()
		f.write("Metano: ")
		f.write(line)
		if check_metano(line) :
			intentos = -1
		else :
			#print "Siguiente intento"
			intentos = intentos - 1
	return line[1:2] 
	
def read_alcohol_arduino():
	global intentos
	s = open_serial_port()
	intentos = 3
	while intentos > 0:
		s.write('A')
                f.write("He pedido A\n")
                time.sleep(1)
		line = s.readline()
		f.write("Alcohol: ")
		f.write(line)
		if check_alcohol(line) :
			intentos = -1
		else :
			#print "Siguiente intento"
			intentos = intentos - 1
	return line[1:2] 
		
def read_pres_arduino():
	global intentos
	s = open_serial_port()
	intentos = 3
	while intentos > 0:
		s.write('P')
                f.write("He pedido P\n")
                time.sleep(1)
		line = s.readline()
		f.write("Presion: ")
		f.write(line)
		if check_value_pres(line) :
			intentos = -1
		else :
			#print "Siguiente intento"
			intentos = intentos - 1
	return line[1:7] #cambiar a line[1:8] para coger 2 decimales

def read_temp_interna():
	s = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
	return s.split('=')[1][:-3]

def escribir_temperaturas(tint, text):
	conn=sqlite3.connect(bd)
	curs=conn.cursor()
	#now = datetime.datetime.now()
	#time = now.strftime("%Y-%m-%d %H:%M:%S")
	#print 'INSERT INTO temps(timestamp,tinterna,texterna) values(?, ?, ?)'
	#print time
	#print tinterna
	#print texterna
	f.write("SQL COMMAND: ")
	f.write("INSERT INTO temps(timestamp,tinterna,texterna) values(")
	f.write(fecha)
	f.write(",")
	f.write(tinterna)
	f.write(",")
	f.write(texterna)
	f.write(")\n")
	curs.execute('INSERT INTO temps(timestamp,tinterna,texterna) values(?, ?, ?)',(fecha, tinterna, texterna))
	conn.commit()
	conn.close()

	
def escribir_humedad(hume):
	conn=sqlite3.connect(bd)
	curs=conn.cursor()
	#now = datetime.datetime.now()
	#time = now.strftime("%Y-%m-%d %H:%M:%S")
	#print 'INSERT INTO hums(timestamp,humedad,) values(?,?)'
	#print time
	#print hume
	f.write("SQL COMMAND: ")
	f.write("INSERT INTO hums(timestamp,humedad) values(")
	f.write(fecha)
	f.write(",")
	f.write(hume)
	f.write(")\n")
	curs.execute('INSERT INTO hums(timestamp,humedad) values(?, ?)',(fecha, hume))
	conn.commit()
	conn.close()
	
def escribir_presion(pres):
	conn=sqlite3.connect(bd)
	curs=conn.cursor()
	#now = datetime.datetime.now()
	#time = now.strftime("%Y-%m-%d %H:%M:%S")
	#print 'INSERT INTO press(timestamp,pres) values(?, ?)'
	#print fecha
	#print pres
	f.write("SQL COMMAND: ")
	f.write("INSERT INTO press(timestamp,pres) values(")
	f.write(fecha)
	f.write(",")
	f.write(pres)
	f.write(")\n")
	curs.execute('INSERT INTO press(timestamp,pres) values(?, ?)',(fecha, pres))
	conn.commit()
	conn.close()

def escribir_bd(tinterna, texterna, pres, hum):
	conn=sqlite3.connect(bd)
	curs=conn.cursor()
        curs.execute('INSERT INTO temps(timestamp,tinterna,texterna) values(?, ?, ?)',(fecha, tinterna, texterna))
        curs.execute('INSERT INTO hums(timestamp,humedad) values(?, ?)',(fecha, hum))
	curs.execute('INSERT INTO press(timestamp,pres) values(?, ?)',(fecha, pres))
	conn.commit()
	conn.close()

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

now = datetime.datetime.now()
fecha = now.strftime("%Y-%m-%d %H:%M:%S")
f.write("Me lanzo\n")
f.write(fecha)
f.write("\n")

actualizar_alertas()
solicitar = False
while not solicitar:
	solicitar = pedir_datos()


if (len(sys.argv) == 1):
	minutos = int(fecha[14:16])
	if minutos%15 == 0 and int(fecha[17:19]) < 25 :
		texterna = read_temp_arduino()
		tinterna = read_temp_interna()
		#checkeo las alertas
		if float(texterna) > 36 and avisoTempExterna == 0 :
 			enviar_aviso("Texterna", texterna)
			cambiar_alerta_sensor("TEXTERNA",1)
		elif float(texterna) <= 36 and avisoTempExterna == 1 :
			cambiar_alerta_sensor("TEXTERNA",0)
      		if float(tinterna) > 60 and avisoTempInterna == 0 :
        		enviar_aviso("Tinterna", tinterna)
           		cambiar_alerta_sensor("TINTERNA",1)
		elif float(tinterna <= 36) and avisoTempInterna == 1 :
           		cambiar_alerta_sensor("TINTERNA",0)
		
		#escribo los datos
		#print "Escribo datos"
		#tinterna = read_temp_interna()
		escribir_bd(tinterna, texterna, presion, humedad)
		
	
	#checkeo alertas alcohol y metano
	if alcohol == 1 and avisoAlcohol == '0' :
		cambiar_alerta_sensor("ALCOHOL",1)
        	enviar_aviso("alcohol", alcohol)
	elif alcohol == 0 and avisoAlcohol == '1' :
		cambiar_alerta_sensor("ALCOHOL",0)
	
	if metano == 1 and avisoMetano == 0 :
		cambiar_alerta_sensor("METANO",1)
        	enviar_aviso("metano", metano)
	elif metano == 0 and avisoMetano == 1 :
		cambiar_alerta_sensor("METANO",0)

else :
	#print "Tiene argumentos"
	if sys.argv[1].startswith('C') or sys.argv[1].startswith('c') :
		if (len(sys.argv[1]) == 9) and ((sys.argv[1][1:2] == '+') or (sys.argv[1][1:2] == '-')) :
			config_arduino(sys.argv[1])

f.close()
