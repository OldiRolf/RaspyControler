
# for external use: 
# from IO_Fkts import Get_Akt_Wert
# from IO_Fkts import Set_Relais
# from IO_Fkts import Get_InPin 
# from IO_Fkts import Close_IO_Fkts


from cmath import pi
import time
from datetime import datetime
from unicodedata import numeric
import serial                                           # RFID
import RPi.GPIO as gpio                                 # Relais und DigitalInputs
import spidev                                           # AD-Wandler
from   w1thermsensor import W1ThermSensor, Sensor       # Temperatur


PIR = 11
####  Initialisierung   #######
gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
gpio.setup(32, gpio.IN) #Set pin as gpio 12 in  / ohne Klemme
gpio.setup(PIR, gpio.IN) #Set pin as gpio 17 in
gpio.setup(12, gpio.IN) #Set pin as gpio 18 in
gpio.setup(13, gpio.IN) #Set pin as gpio 27 in
gpio.setup(15, gpio.IN) #Set pin as gpio 22 in
gpio.setup(16, gpio.IN) #Set pin as gpio 23 in
gpio.setup(18, gpio.IN) #Set pin as gpio 24 in
gpio.setup(22, gpio.IN) #Set pin as gpio 25 in
#gpio.setup( 7 gpio.IN) #1Wire     gpio 04
#in /boot/config.txt : dtoverlay=w1-gpio,gpiopin=4

Relais = [ 0 , 29 , 31 , 33 , 36 , 35 , 38 , 40 , 37 ]
#          0   1     2    3    4    5    6    7    8
gpio.setup(Relais[1], gpio.OUT) #Set pin as gpio 29 out  Releais 1
gpio.setup(Relais[2], gpio.OUT) #Set pin as gpio 31 out  Releais 2
gpio.setup(Relais[3], gpio.OUT) #Set pin as gpio 33 out  Releais 3
gpio.setup(Relais[4], gpio.OUT) #Set pin as gpio 36 out  Releais 4
gpio.setup(Relais[5], gpio.OUT) #Set pin as gpio 35 out  Releais 5
gpio.setup(Relais[6], gpio.OUT) #Set pin as gpio 38 out  Releais 6
gpio.setup(Relais[7], gpio.OUT) #Set pin as gpio 37 out  Releais 7
gpio.setup(Relais[8], gpio.OUT) #Set pin as gpio 40 out  Releais 8


gpio.output(Relais[1],True)
gpio.output(Relais[2],True)
gpio.output(Relais[3],True)
gpio.output(Relais[4],True)
gpio.output(Relais[5],True)
gpio.output(Relais[6],True)
gpio.output(Relais[7],True)
gpio.output(Relais[8],True)

Relais_Setter=[]       # Id (Zeile,Row in Steuertabelle, die Relais bedient, wichtig für PULS-Betrieb )
for i in range(0,9):
    Relais_Setter.append(0)

#RFID:
ser = serial.Serial("/dev/ttyAMA0",timeout = 0)
ser.baudrate = 9600


#DS18S20 Temp:
try:
    sensor = W1ThermSensor(Sensor.DS18S20, "000802b3957b")
except:
    print( 'No Temp-Sensor')

max_temp = 0.0
wait_time = 60 * 5  # 5 Minuten
start_time = 0
last_temp = -99.1

#AD-Wandler MCP3008
spi = spidev.SpiDev()
spi.open(0,1)
spi.max_speed_hz = 5000

CH0 = 0b10000000
CH1 = 0b10010000 
CH2 = 0b10100000 
CH3 = 0b10110000 
CH4 = 0b11000000 
CH5 = 0b11010000 
CH6 = 0b11100000 
CH7 = 0b11110000 

print('Init IO-Fkts',max_temp)

#### 
def Get_Akt_Wert(Quelle):   # Quelle = Wert aus Header aus Steuertabelle (Glt_Von_Dat  .... RFID)
    command = 'Akt_Wert_' + Quelle + '()'
    try:
        x = eval(command)
    except:
        x = 'Error C:' + command
    return x    
  

def Akt_Wert_Glt_Von_Dat():
    return datetime.today().strftime('%m-%d')

def Akt_Wert_Glt_Bis_Dat():
    return datetime.today().strftime('%m-%d')

def Akt_Wert_Glt_Von_Zeit():
    return datetime.today().strftime('%H:%M')

def Akt_Wert_Glt_Bis_Zeit():
    return datetime.today().strftime('%H:%M')

def Akt_Wert_Wochentag():
    tag = ['So','Mo','Di','Mi','Do','Fr','Sa']
    return tag[ int(datetime.today().strftime('%w'))] 


def Akt_Wert_RFID():
    daten = ''
    if ser.in_waiting > 0:
        daten = ser.read(14)
        daten = daten.replace(b'\x02',b'')
        daten = daten.replace(b'\x03',b'')
        daten = str(daten)
        daten = daten[2:14]
    return daten 


def Akt_Wert_Bewegung():
    
    return gpio.input(PIR)


def read_Wert_LUX():
    antwort = spi.xfer([1,CH0,0])
    if 0 <= antwort[1] <= 3 :
        Wert = int(((antwort[1] * 256) + antwort[2]) * 3.22 )  # Spannung ca.  0 - 3000 mV
    return Wert

LUXwerte = []
for i in range (0,10):
    LUXwerte.append(read_Wert_LUX())

def Akt_Wert_LUX():
    LUXwerte.pop(0)
    LUXwerte.append(read_Wert_LUX())
    return int(sum(LUXwerte)/len(LUXwerte))



def read_Wert_Bodenfeuchte():
    antwort = spi.xfer([1,CH1,0])
    if 0 <= antwort[1] <= 3 :
        Wert = 100 - int(((antwort[1] * 256) + antwort[2]) / 10)
    return Wert

Bodenfeuchtewerte=[]
for i in range (0,10):
    Bodenfeuchtewerte.append(read_Wert_Bodenfeuchte())

def Akt_Wert_Bodenfeuchte():
    Bodenfeuchtewerte.pop(0)
    Bodenfeuchtewerte.append(read_Wert_Bodenfeuchte())
    return int(sum(Bodenfeuchtewerte)/len(Bodenfeuchtewerte))



def read_Wert_Wasserstand():
    antwort = spi.xfer([1,CH2,0])
    if 0 <= antwort[1] <= 3 :
        Wert = -0.12445622 * ((antwort[1] * 256) + antwort[2]) + 122.71
    return Wert

Wasserstandswerte = []
for i in range (0,10):
    Wasserstandswerte.append(read_Wert_Wasserstand())

def Akt_Wert_Wasserstand():
    Wasserstandswerte.pop(0)
    Wasserstandswerte.append(read_Wert_Wasserstand())
    return int(sum(Wasserstandswerte) / len(Wasserstandswerte))
    

def Akt_Wert_Temperatur():
    global start_time
    global wait_time
    global max_temp
    global last_temp
    if start_time + wait_time < time.time():
        start_time = time.time()
        #print ('get_temperatur:')
        if datetime.today().strftime('%H:%M') < '00:01' :     # Max-Temp um 0:00 auf 0 setzen
            max_temp = 0.0
        try:      
            #print ('get_temperatur try:')          
            temp = sensor.get_temperature()
            #print ('get_temperatur after try:'   , temp    )    
            try :
                temp = temp * 1.0 
            except:        
                temp = -99.8
        except:
            #print ('get_temperatur except:' , temp )        
            temp = -99.0

        #print ('get_temperatur before set last_temp:'   , last_temp ,'<'   )    
        last_temp = temp
        #print ('get_temperatur after set last_temp:'   , temp    )    
        if temp > max_temp:
            #print ('get_temperatur before set max_temp:'   , temp    )    
            max_temp = temp
 
        #print ('get_temperatur after test max_temp:'   , temp    )    
 
    else:
        temp = last_temp

    #print ('get_temperatur before return:'   , temp    )            
    return temp

def Akt_Wert_MaxTemp():
    return max_temp


def Get_InPin(pin):
    if gpio.input(pin) == 0:
        return 'OFF'
    else:
        #return 'OFF'
        return 'ON'


def Set_Relais(relais,soll,SetterID):
    global Relais_Setter
    
    #while relais > 0:
    #    R=relais%10
    #    relais=relais//10
    if Relais_Setter[relais] == 0 or Relais_Setter[relais] == SetterID:
        if soll == 'ON':
            Relais_Setter[relais] = SetterID              
            gpio.output(Relais[relais],False) 
#            print ('Releais:', relais,soll,SetterID)
        else:  
            Relais_Setter[relais] = 0
            gpio.output(Relais[relais],True) 
#            print ('Releais:', relais,soll,SetterID)
    #else der darf dann nicht, Relais ist schon benutzt
#    else:
#        print ('Releais used:', relais,soll,SetterID)
        
            
def Close_IO_Fkts():
    ser.close() 
