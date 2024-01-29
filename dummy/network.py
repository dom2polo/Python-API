import folium
from folium.plugins import MarkerCluster
from folium import PolyLine, Marker
import pypyodbc as odbc
from pyproj import Proj, transform

# Database connection parameters
DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'dom2polo\\SQLEXPRESS'
DATABASE_NAME = 'transportationdb'

# Assuming Windows Authentication; modify the connection string accordingly for SQL Server authentication
connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes; 
"""

# Connect to the database
conn = odbc.connect(connection_string)

# Query to retrieve coordinates and details for FromId and ToId
query = """
    SELECT 
        ae.[Link] AS Link,
        COALESCE(ae.[Person], asr.[Person], arr.[Person], dep.[Person]) AS Person,
        lnk.[ID] AS LinkID,
        lnk.[FromId] AS LinkFromID,
        lnk.[ToId] AS LinkToID,
        lnk.[Length] AS LinkLength,
        lnk.[Freespeed] AS LinkFreespeed,
        lnk.[Capacity] AS LinkCapacity,
        lnk.[Permlanes] AS LinkPermlanes,
        lnk.[Oneway] AS LinkOneway,
        lnk.[Modes] AS LinkModes,
        nd.[ID] AS NodeID,
        nd.[X] AS NodeX,
        nd.[Y] AS NodeY
    FROM
        [dbo].[ActEnd] ae
    JOIN
        [dbo].[Links] lnk ON ae.[Link] = lnk.[ID]
    JOIN
        [dbo].[ActStart] asr ON ae.[Link] = asr.[Link]
    JOIN
        [dbo].[Arrival] arr ON ae.[Link] = arr.[Link]
    JOIN
        [dbo].[Departure] dep ON ae.[Link] = dep.[Link]
    JOIN
        [dbo].[Nodes] nd ON lnk.[FromId] = nd.[ID] OR lnk.[ToId] = nd.[ID]
"""

# Create a cursor
cursor = conn.cursor()

# Execute the query
cursor.execute(query)

# Fetch data in batches
batch_size = 1000
batch = cursor.fetchmany(batch_size)

# Process all batches on a single map
if batch:
    local_epsg_code = 26915  # Replace with the correct EPSG code for your local coordinate system

    # Create a Pyproj transformer
    transformer = Proj(init=f'epsg:{local_epsg_code}'), Proj(init='epsg:4326')

    # Create a map centered around the first retrieved coordinates with an initial zoom level
    first_from_node_id, first_from_x, first_from_y, first_to_node_id, first_to_x, first_to_y = batch[0][-6:]
    first_from_lon, first_from_lat = transform(transformer[0], transformer[1], first_from_x, first_from_y)
    mymap = folium.Map(location=[first_from_lat, first_from_lon], zoom_start=12)

    # Create a MarkerCluster for markers
    marker_cluster = MarkerCluster().add_to(mymap)

    # Loop through all batches to add markers for each link
    # Loop through all batches to add markers for each link
    for row in batch:
        link, person, link_id, link_from_id, link_to_id, link_length, link_freespeed, link_capacity, link_permlanes, link_oneway, link_modes, node_id, node_x, node_y = row

        # Convert node_x and node_y to scalar values
        node_x_scalar = node_x[0]
        node_y_scalar = node_y[0]

        # Transform coordinates for the 'from' node
        node_lon, node_lat = transform(transformer[0], transformer[1], node_x_scalar, node_y_scalar)

        # Add marker for the 'from' node to the MarkerCluster
        popup_html = f"Link ID: {link_id}<br>Person: {person}<br>Link Length: {link_length}<br>Link Freespeed: {link_freespeed}<br>Link Capacity: {link_capacity}<br>Link Permlanes: {link_permlanes}<br>Link Oneway: {link_oneway}<br>Link Modes: {link_modes}<br>Node ID: {node_id}<br>Latitude: {node_lat}, Longitude: {node_lon}"
        Marker(location=[node_lat, node_lon], popup=folium.Popup(popup_html, parse_html=True), icon=folium.Icon(color='red')).add_to(mymap)

    # Save the map to an HTML file
    map_filename = 'Person_linked_points_map.html'
    mymap.save(map_filename)
    print(f"Map saved to {map_filename}")

# Close the database connection
conn.close()
