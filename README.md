Zu installierende Module:

meshtastic
meshtastic.serial_interface
folium
json

Das Script stellt mittels USB eine Verbindung zu einem Meshtastic-Gerät her, lädt die Knoteninfo herunter und erstellt eine HTML-Datei mit einer Karte, auf der die Knoten, die Koordinaten haben, eingezeichnet sind. Die Farbe der Knoten hängt ab vom SNR. Knoten, die keinen SNR-Wert haben oder deren Hopanzahl > 0 ist, sind schwarz.
