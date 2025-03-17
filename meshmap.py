import meshtastic
import meshtastic.serial_interface
import folium
import json

# Funktion zum Verbinden mit einem Meshtastic-Gerät über die serielle Schnittstelle
def connect_to_device():
    device = meshtastic.serial_interface.SerialInterface()  # Verbindung zum Meshtastic-Gerät herstellen
    return device

# Funktion zum Abrufen aller Knoten des verbundenen Geräts
def get_nodes(device):
    return device.nodes  # Gibt eine Liste der Knoten des Geräts zurück

# Funktion zum Abrufen der Informationen des eigenen Knotens
def get_my_node_info(device):
    my_node = device.getMyNodeInfo()  # Holt Informationen zum eigenen Knoten
    if my_node:
        return my_node.get('num'), my_node  # Gibt die Knoten-ID und die Details zurück
    return None, None  # Wenn keine Informationen vorhanden sind, None zurückgeben

# Funktion zur Umrechnung des SNR (Signal-to-Noise Ratio) in eine Farbe
def snr_to_color(snr, hopsAway):
    if (snr is None) or (hopsAway is not None and hopsAway > 0):  # Wenn SNR nicht vorhanden oder Hops größer als 0, dann schwarz
        return 'black'
    
    snr_scaled = max(min(snr, 10), -20)  # Skaliert SNR zwischen -20 und 10
    
    if snr_scaled <= -10:
        return 'red'  # Sehr schwaches Signal
    elif snr_scaled <= 0:
        return 'orange'  # Mittleres Signal
    elif snr_scaled <= 5:
        return 'lightgreen'  # Gutes Signal
    else:
        return 'green'  # Sehr gutes Signal

# Funktion zum Erstellen der Karte mit den Knoten
def create_map(nodes, my_node_id, my_node_info):
    map_center = [48.4704, 9.2013]  # Zentrale Koordinaten für die Karte (Beispiel)
    m = folium.Map(location=map_center, zoom_start=10)  # Erstellen einer Folium-Karte

    own_node = None  # Variable für den eigenen Knoten
    node_positions = {}  # Dictionary, um Positionen der Knoten zu speichern

    # Iteration über alle Knoten und Hinzufügen von Markern zur Karte
    for node_id, node in nodes.items():
        if 'position' in node:  # Überprüfen, ob der Knoten eine Position hat
            latitude = node['position'].get('latitude', None)
            longitude = node['position'].get('longitude', None)
            if latitude and longitude:
                snr = node.get('snr', None)  # Signalstärke des Knotens
                hopsAway = node.get('hopsAway')  # Hops-Wert des Knotens
                marker_color = snr_to_color(snr, hopsAway)  # Bestimmen der Markerfarbe basierend auf SNR

                if node_id == my_node_id:
                    own_node = (latitude, longitude)  # Position des eigenen Knotens speichern

                # Hinzufügen eines Markers für den Knoten zur Karte
                folium.Marker(
                    location=[latitude, longitude],
                    popup=f"Node ID: {node_id}\n{node['user']['longName']} ({node['user']['shortName']})\nHops: {hopsAway}\nSNR: {snr} dB",
                    icon=folium.Icon(color=marker_color)
                ).add_to(m)

    # Infobox für den eigenen Knoten oben links auf der Karte hinzufügen
    if my_node_info:
        info_html = f"""
        <div style="position: fixed; 
                    top: 10px; left: 10px; width: 250px; height: auto; 
                    background-color: white; z-index:9999; padding: 10px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
            <h4>Eigener Knoten</h4>
            <p><strong>ID:</strong> {my_node_id}</p>
            <p><strong>Name:</strong> {my_node_info['user']['longName']} ({my_node_info['user']['shortName']})</p>
            <p><strong>Battery:</strong> {my_node_info.get('batteryLevel', 'N/A')}%</p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(info_html))  # Fügt die Infobox der Karte hinzu

    m.save("meshtastic_map.html")  # Speichert die Karte als HTML-Datei
    print("Karte wurde erfolgreich erstellt und als 'meshtastic_map.html' gespeichert.")  # Bestätigungsausgabe

# Hauptfunktion zum Verbinden mit dem Gerät, Abrufen von Knoten und Erstellen der Karte
def main():
    device = connect_to_device()  # Verbindung zum Gerät herstellen
    nodes = get_nodes(device)  # Abrufen der Knoten
    my_node_id, my_node_info = get_my_node_info(device)  # Abrufen der Informationen des eigenen Knotens
    create_map(nodes, my_node_id, my_node_info)  # Erstellen der Karte mit den Knoten und dem eigenen Knoten

if __name__ == "__main__":
    main()  # Hauptfunktion ausführen
