import meshtastic
import meshtastic.serial_interface
import folium
import json

# Funktion zum Verbinden mit einem Meshtastic-Device
def connect_to_device():
    # Öffnet eine Verbindung zu einem Meshtastic-Gerät
    device = meshtastic.serial_interface.SerialInterface()  # Passe den Port entsprechend an
    return device

def get_nodes(device):
    # Holt die Knoteninformationen vom Gerät
    nodes = device.nodes
    return nodes

def snr_to_color(snr):
    """Konvertiert SNR-Werte in Farben, von Rot (niedrig) bis Grün (hoch)."""
    # Wenn kein SNR-Wert vorhanden ist, setze die Farbe auf Schwarz
    if snr is None:
        return 'black'
    
    # Skalierung des SNR-Werts auf den Bereich 0 bis 255 (für RGB-Farben)
    # Der SNR-Wert wird von -20 bis 10 auf den Bereich 0 bis 255 skaliert
    snr_scaled = max(min(snr, 10), -20)  # Begrenze den SNR-Wert auf den Bereich [-20, 10]
    
    # Berechne den Farbwert für Rot und Grün
    # -20 ergibt Rot, 10 ergibt Grün
    red = max(0, 255 - int((snr_scaled + 20) * 255 / 30))  # Skalierung von -20 bis 10
    green = max(0, int((snr_scaled + 20) * 255 / 30))  # Skalierung von -20 bis 10
    
    # Bestimme eine Farbe, die von Rot (niedrig) zu Grün (hoch) übergeht
    if snr_scaled <= -10:
        return 'red'
    elif snr_scaled <= 0:
        return 'orange'
    elif snr_scaled <= 5:
        return 'lightgreen'
    else:
        return 'green'

def create_map(nodes):
    # Initialisiere die Karte mit einem mittleren Punkt
    map_center = [48.4704, 9.2013]  # Setze hier einen zentralen Punkt, z. B. Stuttgart, Deutschland
    m = folium.Map(location=map_center, zoom_start=10)

    # Gehe alle Knoten durch und füge sie zur Karte hinzu, falls sie eine Position haben
    for node_id, node in nodes.items():
        if 'position' in node:
            latitude = node['position'].get('latitude', None)
            longitude = node['position'].get('longitude', None)
            if latitude and longitude:
                # Hole den SNR-Wert sicher
                snr = node.get('snr', None)
                
                # Hole den Batteriestatus, falls 'deviceMetrics' existiert
                battery_level = node.get('deviceMetrics', {}).get('batteryLevel', 'unbekannt')

                # Bestimme die Markerfarbe basierend auf dem SNR
                marker_color = snr_to_color(snr)

                # Füge einen Marker mit den Knoteninformationen hinzu
                folium.Marker(
                    location=[latitude, longitude],
                    popup=f"Node ID: {node_id}\n{node['user']['longName']} ({node['user']['shortName']})\nBattery: {battery_level}%\nSNR: {snr} dB",
                    icon=folium.Icon(color=marker_color)
                ).add_to(m)
    
    # Speichere die Karte als HTML-Datei
    m.save("meshtastic_map.html")
    print("Karte wurde erfolgreich erstellt und als 'meshtastic_map.html' gespeichert.")

# Hauptlogik
def main():
    device = connect_to_device()
    nodes = get_nodes(device)
    create_map(nodes)

if __name__ == "__main__":
    main()
