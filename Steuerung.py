#!/usr/bin/python3

#for external use:

#from  Steuerung import refresh_Steuertabelle
#from  Steuerung import get_akt_Wert
#from  Steuerung import get_soll(row)
#from  Steuerung import loop_Steuertabelle
#from  Steuerung import dump_Steuertabelle
#from  Steuerung import write_Header
#from  Steuerung import write_akt_Werte
#from  Steuerung import close_Steuerung
#from  Steuerung import get_modus(row)
#from  Steuerung import set_modus(row,value)


from ast import Break
import csv,time,sys
from telnetlib import theNULL
from multiprocessing.sharedctypes import Value
from datetime import datetime

print (sys.platform)
if sys.platform == 'linux':
    print ('linux')
    from IO_Fkts import Get_Akt_Wert
    from IO_Fkts import Set_Relais
    from IO_Fkts import Get_InPin
    from IO_Fkts import Close_IO_Fkts
    filename_Steuertabelle       = '/mnt/usb1/Garage/Steuertabelle.csv'
    NoNet_filename_Steuertabelle = 'Steuertabelle.csv'
    filename_Logfile             = '/mnt/usb1/Garage/Logs/Sensor_log-' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.csv'
    filename_dump_Steuertabelle  = '/mnt/usb1/Garage/Logs/Steuertabelle' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.csv'

else:   # für Test auf Windowsrechner, wo die Hardware nicht da ist
    def Get_Akt_Wert(Q):
        r = 119.35677
        if Q[0:3] == 'Glt':
            if Q[8:11] == 'Dat':
                r = datetime.now().strftime('%m-%d')
            else:
                r = datetime.now().strftime('%H:%M')
        if Q == 'RFID':
            if time.strftime("%S") == '30':
                r = '294BA---8FCA'
            else:
                r = '------------'
        return r

    def Set_Relais(relais,soll,SetterID):
        return
    def Get_InPin(pin):
        return 'OFF'
    def Close_IO_Fkts():
        return
    print ('win32')
    filename_Steuertabelle       = 'Steuertabelle.csv'
    NoNet_filename_Steuertabelle = 'NoNET_Steuertabelle.csv'
    filename_Logfile             = 'Sensor_log.csv'
    filename_dump_Steuertabelle  = 'Steuertabelle_dump.csv'



""" Aufbau Steuertabelle: 1. Zeile = Header entspricht Steuertabelle[0]
Aktion	    Soll	manuell 	Relais	Aktion	Glt_Von_Dat	Glt_Bis_Dat	Glt_Von_Zeit	Glt_Bis_Zeit	Wochentag   RFID	       LUX	Bewegung	Bodenfeuchte	Wasserstand	Temperatur	MaxTemp 	
Type	    S	    P	        R	    A	    C>	        C<	        C>	            C<	            C           C	           C	    C	        C	            C	        C	        C	
Aktueller Wert																
Tor öffnen	OFF		            1       1                                              					            294BA6818FCA                            		    			        		
Tor öffnen	OFF		            1       1												
Tor öffnen	OFF		            1	    1                                                                                                   				    						
Licht an	OFF		            2   	3000						                                                                <100	1	                            		                		
Teich füll	OFF	    12      	34	    ON	                    		12:00	        13:00					                                                        <115        >7	        > 1		
Regner Wall	OFF	    13	        35	    ON			                    18:00	        19:00				                                            <10			                            >15	
Regner Rts	OFF	    15	        36	    ON	    01-01	    10-01	    07:00	        23:00				                                            <10			                            >15	
Regner Rks	OFF	    16	        37      ON	    05-01	    10-01	    07:00	        08:00				                                            <10			                            >15	
Pumpe	    OFF	    18	        3	    ON												
"""



Steuertabelle = []
def set_Steuertabelle_Wert ( row,col,wert):
    global Steuertabelle
    try:
        Steuertabelle[row][col] = wert
        return 'OK'
    except:
        return 'Index out of range'

def read_tab():
# CSV-Daten in verschachtelte Liste einlesen
    try:
        fi =  open(filename_Steuertabelle )
        cr = csv.reader(fi,delimiter=';')
        for line in cr:
            Steuertabelle.append(line)
        return 'OK'
    except:
        return 'NOK'

def NoNet_read_tab():
# CSV-Daten in verschachtelte Liste einlesen
    try:
        fi =  open(NoNet_filename_Steuertabelle )
        cr = csv.reader(fi,delimiter=';')
        for line in cr:
            Steuertabelle.append(line)
        return 'OK'
    except:
        return 'NOK'

#-------------------------------------------------------------------------------------
##Initialsierung
#Ausprägungen für Modus
K_ON  = 'ON'
K_OFF = 'OFF'
K_AUTO = 'AUTO'

K_TIME_MAX = 999999999999.9

#Spaltentypen
SP_S = 'S'       # Soll
SP_P = 'P'       # Pin manueller Taster
SP_A = 'A'       # Aktion
SP_R = 'R'       # Relaisnr
SP_C = 'C'       # Conditions

Versuch = 1
while read_tab() == 'NOK':
    print (Versuch,' Steuertabelle: ', filename_Steuertabelle , ' konnte nicht gelesen werden!', chr(7))
    time.sleep(5)
    Versuch += 1
    if (NoNet_read_tab() == 'OK') and (Versuch > 10):
        print ('Steuertabelle: ' , NoNet_filename_Steuertabelle , ' wurde gelesen')
        break

# 0 = Headerzeile , 1 = ColtypeZeile , 2 = Zeile für aktuelle Werte , 3....  Aktionen

Anz_Spalten = len(Steuertabelle[0])
Header      = Steuertabelle[0]
ColTypes    = Steuertabelle[1]
Akt_Wert    = Steuertabelle[2]
Aktion_start= 3
Aktion_ende = len(Steuertabelle)

Cond_end_col = len(ColTypes) - 1   # wird für CHANGED gebraucht, nur diese Spalten sind dafür relevant
Cond_start_col = 0
for ColTyp in ColTypes:
    if ColTyp == SP_C:
        break
    Cond_start_col += 1

Modus       = []
Last_Soll   = []
Soll_changetime_of_row = []
#relais_used = ['N','N','N','N','N','N','N','N','N','N','N']
for i in range (0,Aktion_ende ):
    Soll_changetime_of_row.append(K_TIME_MAX)
    Modus.append(K_AUTO)
    Last_Soll.append('-')

def get_modus(row):
    try:
        return Modus[row]
    except:
        return 'not defined'

def set_modus(row,value):
    try:
        Modus[row]=Value
    except:
        print('Error set_modus',row,value)
        return

def get_akt_Wert(sensor):
    return Akt_Wert[Header.index(sensor)]

def get_soll(row):
    return Steuertabelle[row][1]

def refresh_Steuertabelle():
# CSV-Daten in verschachtelte Liste einlesen
    global Steuertabelle
    #Steuertabelle.clear
    try:
        with open(filename_Steuertabelle) as fi:
            cr = csv.reader(fi,delimiter=';')
            i = 0
            for line in cr:
                if i != 2 :   #Akt_Wert nicht überschreiben
                    Steuertabelle[i] = line
                i += 1
        return 'OK'
    except:
        try:
            with open(NoNet_filename_Steuertabelle ) as fi:
                cr = csv.reader(fi,delimiter=';')
                i = 0
                for line in cr:
                    if i != 2 :   #Akt_Wert nicht überschreiben
                        Steuertabelle[i] = line
                    i += 1
            return 'OK Local'
        except:
            return 'NOK'


def dump_Steuertabelle():  # nur für Testzwecke
# CSV-Daten in verschachtelte Liste einlesen
    global Steuertabelle
    try:
        with open(filename_dump_Steuertabelle,'w',encoding='UTF-8') as fo:
            hist = csv.writer(fo,delimiter=';',lineterminator='\n',quoting=csv.QUOTE_NONE)
            hist.writerows(Steuertabelle)
    except:
        return
#-------------------------------------------------------------------------------------
def write_akt_Werte():
#  open file for append
    global Steuertabelle
    try:
        with open(filename_Logfile ,'a',encoding='UTF-8') as fo:
            hist = csv.writer(fo,delimiter=';',dialect='excel',lineterminator='\n')
            Akt_Wert[0] = datetime.now()
            lista = list(Akt_Wert)
            listb = (Steuertabelle[3][1],Steuertabelle[4][1],Steuertabelle[5][1],Steuertabelle[6][1],Steuertabelle[7][1],Steuertabelle[8][1],Steuertabelle[9][1],Steuertabelle[10][1],Steuertabelle[11][1])
            lista.extend(listb)
            lista.extend(Modus[3:len(Modus)])
            hist.writerow(lista)
        return 'open ' + filename_Logfile
    except:
        return filename_Logfile + ' not open'


def write_Header():
#  open new file
    global Steuertabelle
    try:
        with open(filename_Logfile ,'w',encoding='UTF-8') as fo:
            hist = csv.writer(fo,delimiter=';',dialect='excel',lineterminator='\n')
            lista = list(Steuertabelle[0])
            listb = [Steuertabelle[3][0],Steuertabelle[4][0],Steuertabelle[5][0],Steuertabelle[6][0],Steuertabelle[7][0],Steuertabelle[8][0],Steuertabelle[9][0],Steuertabelle[10][0],Steuertabelle[11][0]]
            lista.extend(listb)
            lista.extend(listb)
            hist.writerow(lista)
        return 'open ' + filename_Logfile
    except:
        return filename_Logfile + ' not open'



def Get_Akt_Werte():
    global Header, Akt_Wert , ColTypes ,Steuertabelle

    i = 0
    for ColTyp in ColTypes:
        #x = ''
        if ColTyp[0] == SP_C:
            Akt_Wert[i] = Get_Akt_Wert(Header[i])
#            if Header[i] == 'RFID':
#                print('Get_Akt_Werte:',Akt_Wert[i] ,'>', Steuertabelle[2][i],'<','>', Steuertabelle[0][i],'<')

        i += 1
    return


def Get_result(Wert,Cond,ColTyp):

    global K_ON, K_OFF , K_AUTO
    global SP_A , SP_C , SP_S, SP_P, SP_R
    try:
        if len(ColTyp) == 2:
            if   ColTyp[1] == '>':
                if Wert >= Cond:
                    return K_ON
                else:
                    return K_OFF
            else:
                if Wert <= Cond:
                    return K_ON
                else:
                    return K_OFF
        else:
            if   Cond[0] == '>':
                if Wert > int(Cond[1:]):
                    return K_ON
                else:
                    return K_OFF
            elif Cond[0] == '<':
                if Wert < int(Cond[1:]):
                    return K_ON
                else:
                    return K_OFF
            else:
                if Wert == Cond:
                    return K_ON
                else:
                    return K_OFF
    except:
        X =  'ERR: ' + str(Wert) + ' ' + Cond

    return X

def is_int(wert):
    try:
        X=int(wert)
        return True
    except:
        return False


def Set_Soll_of_row(row):
    global Soll_changetime_of_row , Modus
    global Steuertabelle
    global Akt_Wert , ColTypes , Last_Soll
    #global K_ON, K_OFF , K_AUTO
    #global SP_A , SP_C , SP_S, SP_P, SP_R

    i = 0
    s = 0

    spalten=Steuertabelle[row]
#    print (row , spalten[s], '--------' ,time.time() - Soll_changetime_of_row[row])

    if s == 'XXX' and Soll_changetime_of_row[row] < K_TIME_MAX and Last_Soll[row] == K_ON:  # Aktion is running
        Soll = Last_Soll[row]
        print('Aktion ' + spalten[0]  +  ' is running')
    else:
        for ColTyp in ColTypes:
            if  ColTyp == SP_S:
                s =  i
                Soll = '-'
                Last_Soll[row]=spalten[s]

            if ColTyp == SP_P:
                if is_int(spalten[i]):
                    # print (row , spalten[i], Get_InPin(int(spalten[i])) ,time.time() - Soll_changetime_of_row[row],Soll_changetime_of_row[row],spalten[s],Modus[row])
                    if Get_InPin(int(spalten[i])) == K_ON:  #
                        if  Modus[row] == K_AUTO and spalten[s] == K_OFF and Soll_changetime_of_row[row] == K_TIME_MAX:
                            Modus[row] = K_ON
                            Soll_changetime_of_row[row] = time.time()

                        elif Modus[row] == K_AUTO and spalten[s] == K_ON and Soll_changetime_of_row[row] == K_TIME_MAX:
                            Modus[row] = K_OFF
                            Soll_changetime_of_row[row] = time.time()

                        elif Modus[row] == K_OFF  and Soll_changetime_of_row[row] == K_TIME_MAX:
                            Modus[row] = K_ON
                            Soll_changetime_of_row[row] = time.time()

                        elif Modus[row] == K_ON  and Soll_changetime_of_row[row] == K_TIME_MAX:
                            Modus[row] = K_OFF
                            Soll_changetime_of_row[row] = time.time()

                        elif time.time() - Soll_changetime_of_row[row] > 2.0:
                            Modus[row] = K_AUTO
                            #Soll_changetime_of_row[row] = K_TIME_MAX

                    elif time.time() - Soll_changetime_of_row[row] > 2.0:
                        Soll_changetime_of_row[row] = K_TIME_MAX
                #else:
                #    print (row , spalten[i], ' ---- ',time.time() - Soll_changetime_of_row[row])


            if ColTyp[0] == SP_C:   # 'C'  , 'C>' ,  'C<'
                if Modus[row] != K_AUTO:
                    Soll = Modus[row]
                    break

                C = Soll                                           # Initial Spalte S   --> '-'
                if  spalten[i] > '':
                    C = Get_result(Akt_Wert[i],spalten[i],ColTyp)  #  --> K_ON / K_OFF
    #                if row == 3:
    #                    print('Get_result(',Akt_Wert[i],spalten[i],ColTyp,'-->',C)  #  --> K_ON / K_OFF

                if  Soll == K_ON and C == K_OFF :  #
                    Soll = K_OFF
                elif Soll == '-' :  # eine Result K_ON darf ein Soll K_OFF nicht auf K_ON setzen
                                    #  AND-Verknüpfung aller CONDs einer Zeile !!
                    Soll = C        #

            i += 1

    changed = (Soll != Last_Soll[row])
    Steuertabelle[row][s] = Soll
    return changed


def Do_Aktion_of_row(row):
    global Soll_changetime_of_row , Modus #, relais_used
    global Steuertabelle
    global Akt_Wert , ColTypes , Last_Soll
    global K_ON, K_OFF , K_AUTO
    global SP_A , SP_C , SP_S, SP_P, SP_R
    i = 0

#    print(Steuertabelle[2][0],Steuertabelle[0][9],Steuertabelle[2][9],Steuertabelle[3][1],Steuertabelle[4][1],Steuertabelle[5][1])

    spalten=Steuertabelle[row]
    for ColTyp in ColTypes:
        #print(i,'ColTyp:',ColTyp)
        if  ColTyp == SP_S:
            Soll = spalten[i]
            S = i

        if ColTyp == SP_R:
            if is_int(spalten[i]):
                relais=int(spalten[i])
#                print(relais_used)
#                if relais_used[relais] != 'N' :
#                    if relais_used[relais] != row :
#                        break
            else:
                relais=-1

        if ColTyp == SP_A:
            if spalten[i] > '':
                aktion = spalten[i]
                if Soll == K_ON:
                    if is_int(aktion) :
                        sct= Soll_changetime_of_row[row]
                        if  sct == K_TIME_MAX:
                            Soll_changetime_of_row[row] = time.time()
                            Set_Relais(relais,Soll,row)
                        elif sct + float(aktion) <= time.time():
                            Set_Relais(relais,K_OFF,row)
                            Steuertabelle[row][S] = K_OFF
                            Soll_changetime_of_row[row] = K_TIME_MAX
 #                       print ('Aktion0:', aktion,  relais, Soll ,row ,sct )
                    else:
                        Set_Relais(relais,Soll,row)
 #                       print ('Aktion1:', aktion,  relais, Soll ,row  )
                  #  relais_used[relais] = row
                else:
                    Set_Relais(relais,Soll,row)
 #                   print ('Aktion2:' , aktion,  relais, Soll ,row  )
                  #  relais_used[relais] = 'N'
            break  # Bedingungen nicht mehr abfragen

        i += 1

    changed = (Soll != Steuertabelle[row][S])
    return changed

def loop_Steuertabelle():
    global Steuertabelle, Akt_Wert, Cond_end_col,Cond_start_col

    changed = False
    #Aktuelle Wert für Conditions        ersten 4 DATUM/Zeit übersrpingen, sonst jede Minute eine Änderung !


    Last_Akt_Wert = list(Akt_Wert[Cond_start_col :Cond_end_col])

    Get_Akt_Werte()
    changed = (Last_Akt_Wert != Akt_Wert[Cond_start_col:Cond_end_col])

    for i in range(Aktion_start,Aktion_ende):
        if Set_Soll_of_row(i):
            changed = True
        if Do_Aktion_of_row(i):
            changed = True

    return changed

def close_Steuerung():
    Close_IO_Fkts()