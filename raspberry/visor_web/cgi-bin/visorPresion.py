#!/usr/bin/env python

import sqlite3
import sys
import cgi
import cgitb


# global variables
speriod=(15*60)-1
dbname='/var/www/templogCompleto.db'


# print the HTTP header
def printHTTPheader():
    print "Content-type: text/html\n\n"



# print the HTML head section
# arguments are the page title and the table for the chart
def printHTMLHead(title, table):
    print "<head>"
    print "    <title>"
    print title
    print "    </title>"
    print "<link rel='stylesheet' type='text/css' href='http://158.49.250.145/css/style.css'>"
    print "<meta http-equiv='refresh' content='900'> <!-- Refresh every 15 minutes -->"    
    print "<link rel='shortcut icon' href='http://158.49.250.145/images/laruex_favicon.ico'/>"
    print '<link rel="shortcut icon" sizes="196x196" href="http://158.49.250.145/images/icon-196x196.png">'
    print '<link rel="apple-touch-icon" href="http://158.49.250.145/images/icon-57x57.png"/>'
    print '<link rel="apple-touch-icon" sizes="72x72" href="http://158.49.250.145/images/icon-72x72.png" />'
    print '<link rel="apple-touch-icon" sizes="114x114" href="http://158.49.250.145/images/icon-114x114.png" />'
    print '<meta name="mobile-web-app-capable" content="yes">'
    print '<meta name="apple-mobile-web-app-capable" content="yes">'
    print_graph_script(table)

    print "</head>"


# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_data(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT * FROM press")
    else:
        curs.execute("SELECT * FROM press WHERE timestamp>datetime('now','-%s hours')" % interval)
#        curs.execute("SELECT * FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hours') AND timestamp<=datetime('2013-09-19 21:31:02')" % interval)

    rows=curs.fetchall()

    conn.close()

    return rows


# convert rows from database into a javascript table
def create_table(rows):
    chart_table=""

    for row in rows[:-1]:
        rowstr="['{0}', {1}],\n".format(str(row[0]),str(row[1]))
        chart_table+=rowstr

    row=rows[-1]
    rowstr="['{0}', {1}]\n".format(str(row[0]),str(row[1]))
    chart_table+=rowstr

    return chart_table


# print the javascript to generate the chart
# pass the table generated from the database info
def print_graph_script(table):

    # google chart snippet
    chart_code="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Time', 'Presion'],
%s
        ]);

        var options = {
          title: 'Presion'
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>"""

    print chart_code % (table)




# print the div that contains the graph
def show_graph():
    print "<h2>Presion Chart</h2>"
    print '<center><div id="chart_div" style="width: 900px; height: 500px;"></div></center>'

def choose_bar(num):
    if (num < 1200):
        print "<div class='meter green stripes'>"
    elif (num < 1700):
        print "<div class='meter orange stripes'>"
    else:
        print "<div class='meter red stripes'>"


# connect to the db and show some stats
# argument option is the number of hours
def show_stats(option):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if option is None:
        option = str(24)

    curs.execute("SELECT timestamp,max(pres) FROM press WHERE timestamp>datetime('now','-%s hours')" % option)
    rowmax=curs.fetchone()
    rowstrmax="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmax[0]),str(rowmax[1]))

    curs.execute("SELECT timestamp,min(pres) FROM press WHERE timestamp>datetime('now','-%s hours')" % option)
    rowmin=curs.fetchone()
    rowstrmin="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmin[0]),str(rowmin[1]))

    curs.execute("SELECT avg(pres) FROM press WHERE timestamp>datetime('now','-%s hours')" % option)
    rowavg=curs.fetchone()

    print "<hr>"

    print "<div id='values'>"

    print "<div id='min_temp' class='inline'>"
    print "<h2>Presion  Minima&nbsp</h2>"
    min_percent = str(rowmin[1])[0:4]
    choose_bar(float(min_percent))
    min_percent = str(float(min_percent)/20)
    print "<span style='width:"+min_percent+"%'></span></div>"
    print rowstrmin+"mb"
    print "</div>"
    
    print "<div id='max_temp' class='inline'>"
    print "<h2>Presion Maxima</h2>"
    max_percent = str(rowmax[1])[0:4]
    choose_bar(float(max_percent))
    max_percent = str(float(max_percent)/20)
    print "<span style='width:"+max_percent+"%'></span></div>"
    print rowstrmax+"mb"
    print "</div>"
    
    print "<div id='avg_temp' class='inline'>"
    print "<h2>Presion Media</h2>"
    avg_percent = str(rowavg[0])[0:4]
    choose_bar(float(avg_percent))
    avg_percent = str(float(avg_percent)/20)
    print "<span style='width:"+avg_percent+"%'></span></div>"
    print "%.3f" % rowavg+"mb"
    print "</div>"

    print "</div>"
    
    print "<div class='clear'></div>"    
    print "<hr>"

    print "<div id='leyenda'>Rangos: Verde: &lt1200 &nbsp Naranja: 1200&ltx&lt1700 &nbsp Rojo: &gt1700 </div>"


    conn.close()




def print_time_selector(option):

    print """<form action="/cgi-bin/visorPresion.py" method="POST">
        Mostrar graficas para un periodo de   
        <select name="timeinterval">"""


    if option is not None:

	if option == "1":
            print "<option value=\"1\" selected=\"selected\">ultima hora</option>"
        else:
            print "<option value=\"1\">ultima hora</option>"

        if option == "6":
            print "<option value=\"6\" selected=\"selected\">ultimas 6 horas</option>"
        else:
            print "<option value=\"6\">ultimas 6 horas</option>"

        if option == "12":
            print "<option value=\"12\" selected=\"selected\">ultimas 12 horas</option>"
        else:
            print "<option value=\"12\">ultimas 12 horas</option>"

        if option == "24":
            print "<option value=\"24\" selected=\"selected\">ultimas 24 horas</option>"
        else:
            print "<option value=\"24\">the last 24 hours</option>"

	if option == "168":
            print "<option value=\"168\" selected=\"selected\">ultima semana</option>"
        else:
            print "<option value=\"168\">ultima semana</option>"
	if option == "720":
            print "<option value=\"720\" selected=\"selected\">ultimo mes</option>"
        else:
            print "<option value=\"720\">ultimo mes</option>"
	
    else:
        print """<option value="720">the last month</option>
	    <option value="168">the last week</option>
	    <option value="6">the last 6 hours</option>
            <option value="12">the last 12 hours</option>
            <option value="24" selected="selected">the last 24 hours</option>"""

    print """        </select>
        <input type="submit" value="Display">
    </form>"""


# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
    # check that the option string represents a number
    if option_str.isalnum():
        # check that the option is within a specific range
        if int(option_str) > 0 and int(option_str) <= 720:
            return option_str
        else:
            return None
    else: 
        return None


#return the option passed to the script
def get_option():
    form=cgi.FieldStorage()
    if "timeinterval" in form:
        option = form["timeinterval"].value
        return validate_input (option)
    else:
        return None




# main function
# This is where the program starts 
def main():

    cgitb.enable()

    # get options that may have been passed to this script
    option=get_option()

    if option is None:
        option = str(24)

    # get data from the database
    records=get_data(option)
    interval2 = option

    # print the HTTP header
    printHTTPheader()

    if len(records) != 0:
        # convert the data into a table
        table=create_table(records)
    else:
        print "No data found"
        return

    # start printing the page
    print "<html>"
    # print the head section including the table
    # used by the javascript for the chart
    printHTMLHead("Presion LARUEX WorkStation", table)

    # print the page body
    print "<body>"
    print "<h1>Presion LARUEX WorkStation <a id='ref_volver' href='main.py'><img id='icono_volver' src='http://158.49.250.145/images/back.png' alt='Volver'></a></h1>"
    print "<hr>"
    print_time_selector(option)
    show_graph()
    show_stats(option)
    print "</body>"
    print "</html>"

    sys.stdout.flush()

if __name__=="__main__":
    main()




