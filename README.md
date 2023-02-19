# RaspyControler
universelles Steuerprogramm für Raspberry (Haus/Garten)  // universal control program to manage house and garden

Die Hardware:
![alt text](https://github.com/OldiRolf/RaspyControler/blob/main/Raspberry%20Pi%20with%20protoshield%20and%20relais%20extension.png?raw=true)

Hier will ich mein Projekt mal veröffentlichen und ggf. weiterentwickeln.
Es handelt sich um einen RaspberryPi, der verschiedene Funktionen wie Bewässerung, Beleuchtung, Tor öffnen , ...  steuern soll.
Welche Funktion unter welchen Bedingungen gestartet wird, wird in einer Excel-Tabelle, die als CSV-Datei gespeichert wird, festgelegt.

![alt text](https://github.com/OldiRolf/RaspyControler/blob/main/Steuertabelle.png?raw=true)

Diese wird vom  Program pro Minute einmal eingelesen, so dass die Änderungen spätestens nach einer Minute wirksam werden. 
Im Wesentlichen beschreibt die Tabelle Aktionen (Spalten A-E) und deren Conditions (Spalten F-Q), die erfüllt sein müssen, damit die Aktion ausgeführt wird.

Besipiele:  Aktion / Bedingung
    
Pumpe (Zeile 12) wird Relais 3 einschalten, 
  wenn Datum >= 1.Januar und <= 31.Dezember 
  Und es zwischen 7:00 und 22:00 ist – also das ganze Jahr zwischen 7Uhr und 22Uhr

Regner Rasen rechts (Zeile 10) wird Relais 7 einschalten,
 	wenn Datum >= 1.Mai und <= 31.Oktober
 	und es Montags ist
 	und von 7:30 bis 8:00 
 	und die Bodenfeuchte unter 90 
 	und die Tageshöchsttemperatur > 15Grad ist

Tor oeffnen (Zeile 4) wird Relais 1 für 1 Sekunde eingeschaltet,
	wenn der RFID-Controller den Wert ……….. empfängt.

Natürlich kann man das Ganze auch über ein Datenbanktabelle machen, aber deshalb eine Datenbank mit SQL etc. installieren und laufen lassen, verbraucht ziemlich viel Rescourcen und Datenbank-Features werden hier nicht benötigt – wir arbeiten die Tabelle rein sequentiell ab. Vorteil dieser Methode ist die Einfachheit und das diese einfach von anderen Rechnern aus gesteuert werden kann, in dem die CSV-Datei einfach auch einem Netzlaufwerk liegt.

Welche Aktionen und Bedingungen es gibt, hängt natürlich von der Beschaltung des Controllers ab. Die erste Zeile in der Tabelle enthält die Namen der Funktionen, die von Steuerung.py aus IO_Fkts.py aufgerufen werden. Somit ist Steuerung.py nicht starr für meine Konfiguration gebunden, sonder flexibel für alle möglichen Anwendungsfälle geeignet, bei denen andere Sensoren und Aktoren zum Einsatz kommen. 

Dies sind meine ersten GitHub Aktivitäten. 
Das Programm ist in der Grundversion schon seid ca. einem Jahr in Einsatz.
