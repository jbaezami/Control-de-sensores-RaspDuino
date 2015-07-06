#!/usr/bin/env python

import cgi
import cgitb
import sys
import os


def printHead():
	print "Content-type: text/html\n\n"
	print "<html><head><title>Redireccion</title></head>"

def bodyTemp():
	print '<body onload='
	print '"window.location='
	print "'http://158.49.111.143/cgi-bin/visorTemperatura.py'"
	print '"></body></html>'

def bodyHum():
        print '<body onload='
        print '"window.location='
        print "'http://158.49.111.143/cgi-bin/visorHumedad.py'"
        print '"></body></html>'

def bodyPres():
        print '<body onload='
        print '"window.location='
        print "'http://158.49.111.143/cgi-bin/visorPresion.py'"
        print '"></body></html>'


def bodyReinicio():
	print '<body onload='
        print '"window.location='
        print "'http://158.49.111.143/'"
        print '"></body></html>'
	os.system('reboot now')

def main():
	
	cgitb.enable()
	form=cgi.FieldStorage()
	printHead()	
	if form["funcionalidad"].value == "temperatura":
		bodyTemp()	
	elif form["funcionalidad"].value == "humedad":
		bodyHum()
        elif form["funcionalidad"].value == "presion":
                bodyPres()
        elif form["funcionalidad"].value == "reiniciar":
                bodyReinicio()
	sys.stdout.flush()


if __name__=="__main__":
    main()

