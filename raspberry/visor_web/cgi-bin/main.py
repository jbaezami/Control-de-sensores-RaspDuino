#!/usr/bin/env python

import cgi
import cgitb
import sys
import os
import sqlite3

dbname='/var/www/templogCompleto.db'
fecha = ""

def printHead():
	print "Content-type: text/html\n\n"
	print "<html><head><title>LARUEX WorkStation</title><link rel='shortcut icon' href='http://158.49.250.145/images/favicon.ico'/>" 
	print "<link rel='stylesheet' type='text/css' href='http://158.49.250.145/css/style.css'>"
	print "<meta http-equiv='refresh' content='30'>"
	print "<link rel='shortcut icon' sizes='196x196' href='http://158.49.250.145/images/icon-196x196.png'>"
	print "<link rel='apple-touch-icon' href='http://158.49.250.145/images/icon-57x57.png'/>"
	print "<link rel='apple-touch-icon' sizes='72x72' href='http://158.49.250.145/images/icon-72x72.png' />"
	print "<link rel='apple-touch-icon' sizes='114x114' href='http://158.49.250.145/images/icon-114x114.png' />"
	print "<meta name='mobile-web-app-capable' content='yes'><meta name='apple-mobile-web-app-capable' content='yes'>"
	print "<style>body{margin-top:20px}</style>"
        print '<script type="text/javascript" language="javascript">'
	print "var seconds = 30;"
	print "var temp;"
	print "function countdown() {"
#	print "window.alert('hola');"
	print "if (seconds == 1) {"
	print "temp = document.getElementById('actualizar');"
	print 'temp.innerHTML = "Actualizar";'
	print "return;}"
	print "seconds--;"
	print "temp = document.getElementById('actualizar');"
	print "temp.innerHTML = 'Actualiza en <br>' + seconds + ' seg.';"
	print "timeoutMyOswego = setTimeout(countdown, 1000); }" 
	print '</script>'

def showTemperatura():
	global fecha
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
    	curs.execute("SELECT max(timestamp),texterna FROM temps")
    	rowmax=curs.fetchone()
	fecha = str(rowmax[0])
    	print "{0} C ".format(str(rowmax[1]))
	conn.close()

def showTemperatura2():
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("SELECT max(timestamp),tinterna FROM temps")
	rowmax=curs.fetchone()
	print "{0} C ".format(str(rowmax[1]))
	conn.close()

def showHumedad():
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()
        curs.execute("SELECT max(timestamp),humedad FROM hums")
        rowmax=curs.fetchone()
        print "{0} % ".format(str(rowmax[1]))
        conn.close()

def showPresion():
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()
        curs.execute("SELECT max(timestamp),pres FROM press")
        rowmax=curs.fetchone()
        print "{0} mb ".format(str(rowmax[1]))
        conn.close()

def showMetano():
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()
        curs.execute("SELECT valor FROM sensores WHERE sensor='METANO'")
        rowmax=curs.fetchone()
	if rowmax[0] == 0:
		print "<div class='states_green'>Metano: <br><hr> OK "
	else:
		print "<div class='states_red'>Metano: <br><hr> ALERTA "
        conn.close()

def showAlcohol():
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()
        curs.execute("SELECT valor FROM sensores WHERE sensor='ALCOHOL'")
        rowmax=curs.fetchone()
        if rowmax[0] == 0:
                print "<div class='states_green'>Alcohol: <br><hr> OK "
        else:
                print "<div class='states_red'>Alcohol: <br><hr> ALERTA "
        conn.close()

def body():
	print "<body onload='countdown()'><a href='http://workstationlaruex.noip.me/' id='actualizar' class='butActualizar'>Actualiza en <br> 30 seg</a></br><img id='icono_laruex' src='http://158.49.250.145/images/icon-196x196.png' alt='LARUEX'><br><br><h1>Bienvenido a LARUEX Raspberry WorkStation</h1>"
	print '<div class="states">T externa:<br><hr>'
	showTemperatura()
	print '</div>'
        print '<div class="states">T interna:<br><hr>'
	showTemperatura2()
	print '</div>'
	print '<div class="states">Humedad:<br><hr>'
        showHumedad()
        print '</div>'
        print '<div class="states">Presi&oacute;n:<br><hr>'
        showPresion()
        print '</div>'
	print "</br>"
	print "Datos actualizados cada 15 minutos. Fecha de ultimos datos: "
        print fecha
        print "</br>"
        showMetano()
	print '</div>'
        showAlcohol()
        print '</div>'

	print '<div id="botones"><input id="envio" name="funcionalidad" value="" hidden/>'
	print '<a class="myButton"'
	print 'href="visorTemperatura.py">Temperatura</a>'
        print '<a class="myButton"'
        print 'href="visorHumedad.py">Humedad</a>'
        print '<a class="myButton"'
        print 'href="visorPresion.py">Presi&oacute;n</a>'
	print "</div></body></html>"

def main():
	
	cgitb.enable()
	form=cgi.FieldStorage()
	printHead()	
	body()
	sys.stdout.flush()


if __name__=="__main__":
    main()

