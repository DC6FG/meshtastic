import meshtastic
import meshtastic.serial_interface
import folium
import json

def connect_to_device():
    device = meshtastic.serial_interface.SerialInterface()
    return device

def get_nodes(device):
    return device.nodes

def get_my_node_info(device):
    my_node = device.getMyNodeInfo()
    if my_node:
        return my_node.get('num'), my_node
    return None, None

def snr_to_color(snr, hopsAway):
    if (snr is None) or (hopsAway is not None and hopsAway > 0):
        return 'black'
    
    snr_scaled = max(min(snr, 10), -20)  
    
    if snr_scaled <= -10:
        return 'red'
    elif snr_scaled <= 0:
        return 'orange'
    elif snr_scaled <= 5:
        return 'lightgreen'
    else:
        return 'green'

def create_map(nodes, my_node_id, my_node_info):
    map_center = [48.4704, 9.2013]  
    m = folium.Map(location=map_center, zoom_start=10)

    own_node = None
    node_positions = {}

    for node_id, node in nodes.items():
        if 'position' in node:
            latitude = node['position'].get('latitude', None)
            longitude = node['position'].get('longitude', None)
            if latitude and longitude:
                snr = node.get('snr', None)
                hopsAway = node.get('hopsAway')
                marker_color = snr_to_color(snr, hopsAway)

                if hopsAway == 0:
                    node_positions[node_id] = (latitude, longitude, marker_color)

                if node_id == my_node_id:
                    own_node = (latitude, longitude)

                folium.Marker(
                    location=[latitude, longitude],
                    popup=f"Node ID: {node_id}\n{node['user']['longName']} ({node['user']['shortName']})\nHops: {hopsAway}\nSNR: {snr} dB",
                    icon=folium.Icon(color=marker_color)
                ).add_to(m)

    if own_node:
        for node_id, (lat, lon, color) in node_positions.items():
            folium.PolyLine(
                locations=[own_node, (lat, lon)],
                color=color,
                weight=2,
                opacity=0.7
            ).add_to(m)

    # Infobox für den eigenen Node hinzufügen
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
        m.get_root().html.add_child(folium.Element(info_html))

    m.save("meshtastic_map.html")
    print("Karte wurde erfolgreich erstellt und als 'meshtastic_map.html' gespeichert.")

def main():
    device = connect_to_device()
    nodes = get_nodes(device)
    my_node_id, my_node_info = get_my_node_info(device)
    create_map(nodes, my_node_id, my_node_info)

if __name__ == "__main__":
    main()
