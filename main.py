#!/usr/bin/python3
# -*- coding: utf-8 -*-
print('Starting')
from operator import truediv
import sys
import time

from  Steuerung import refresh_Steuertabelle
from  Steuerung import loop_Steuertabelle
from  Steuerung import close_Steuerung
from  Steuerung import write_Header
from  Steuerung import write_akt_Werte

from  Steuerung import get_soll
from  Steuerung import get_modus
from  Steuerung import get_akt_Wert
from  Steuerung import Steuertabelle,Modus
from  Steuerung import set_Steuertabelle_Wert
from  Steuerung import Aktion_start,Aktion_ende

#sys.stdout = open('stdlogfile.txt', 'w')


html_start = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//DE"><html>	<head><meta http-equiv="refresh" content="1"><title>Garage</title>	</head>	<body>	<table>'
html_abschluss = '</table></body>	</html>'
html_row_s = '<tr><th align="left"><font  face ="consolas" size="5" font color = "Red">'
html_row_n1 = '</th><th align="right"><font  face ="consolas" size="5" font color = "Red">'
html_row_n2 = '</th><th align="left"><font  face ="consolas" size="5" font color = "Red">'
html_row_e = '</th></tr>' 


loop=0
def steuerung():
    global loop

    if time.strftime("%S") == '00' and loop % 2 == 0:   #Steuertabelle refreshen , jede volle Minute und in Akt_Werte = Steuertabelle[2] eintragen
      print (loop,'refreshing')
      set_Steuertabelle_Wert(2,1,'refresh')
      set_Steuertabelle_Wert(2,2,refresh_Steuertabelle())
      set_Steuertabelle_Wert(2,3,loop)
      x = loop_Steuertabelle()
      print(loop,write_akt_Werte())

    elif time.strftime("%S") == '01':
      set_Steuertabelle_Wert(2,1,'')
      set_Steuertabelle_Wert(2,2,'')
      set_Steuertabelle_Wert(2,3,loop)
      if loop_Steuertabelle():
        print(loop,write_akt_Werte())
        
    else:
      if loop_Steuertabelle():
        print(loop,write_akt_Werte())

    if sys.platform == 'linux':
      html_file = '/var/www/mycode/index.html'    
    else:  
      html_file = 'D:\Temp\index.html'    

    with open( html_file,'w',encoding='cp1252') as html:
        html.write(html_start + '\n') 
        html.write(html_row_s + 'Uhrzeit      :'  + html_row_n1 + time.strftime("%H:%M:%S") + html_row_n2 + ' ' + html_row_e + '\n') 
        html.write(html_row_s + 'Temperatur   :'  + html_row_n1 +'    %.1f' % get_akt_Wert('Temperatur') + html_row_n2 + '°C' + html_row_e + '\n') 
        html.write(html_row_s + 'Max. Temp.   :'  + html_row_n1 +'    %.1f' % get_akt_Wert('MaxTemp ') + html_row_n2 + '°C' + html_row_e + '\n') 
        html.write(html_row_s + 'Wasserstand  :'  + html_row_n1 +'    %.1f' % get_akt_Wert('Wasserstand') + html_row_n2 + 'mm' + html_row_e + '\n') 
        html.write(html_row_s + 'Bodenfeuchte :'  + html_row_n1 +'    %.1f' % get_akt_Wert('Bodenfeuchte') + html_row_n2 + '%' + html_row_e + '\n') 
        html.write(html_row_s + ' '  + html_row_n1 +'' + html_row_n2 + '' + html_row_e + '\n') 
        html.write(html_row_s + 'Aktionen'  + html_row_n1 +'' + html_row_n2 + '' + html_row_e + '\n') 
        html.write(html_row_s + 'Teich füllen :'  + html_row_n1 + get_soll(7) + html_row_n2 + get_modus(7) + html_row_e + '\n') 
        html.write(html_row_s + 'Regner Wall  :'  + html_row_n1 + get_soll(8) + html_row_n2 + get_modus(8) + html_row_e + '\n') 
        html.write(html_row_s + 'Regner rechts:'  + html_row_n1 + get_soll(9) + html_row_n2 + get_modus(9) + html_row_e + '\n') 
        html.write(html_row_s + 'Regner links :'  + html_row_n1 + get_soll(10) + html_row_n2 + get_modus(10) + html_row_e + '\n') 
        html.write(html_row_s + 'Pumpe        :'  + html_row_n1 + get_soll(11) + html_row_n2 + get_modus(11) + html_row_e + '\n') 
        html.write(html_abschluss + '\n') 
        html.close


#start
refresh_Steuertabelle()   #Ist_Quelle initialisieren
print (loop,write_Header())
x = loop_Steuertabelle()
print(loop,write_akt_Werte())

# never ending
while True:
    loop += 1
    print(time.strftime("%H:%M:%S"),loop)
    steuerung()
    time.sleep(0.5)

