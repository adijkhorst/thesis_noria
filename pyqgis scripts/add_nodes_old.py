from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsVectorFileWriter, QgsProject, QgsWkbTypes
from PyQt5.QtCore import QVariant
from qgis.gui import QgsMapCanvas
from qgis import processing


# Specify the path to your GeoJSON file
geojson_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_fewnodes_singleparts.geojson"

# Specify the threshold length (X meters)
threshold_length = 50  # Change this value to your desired length

# Open the GeoJSON layer
line_layer = iface.addVectorLayer(geojson_path, 'LineLayer', 'ogr')

# Print layer information for debugging
print(f'Layer name: {line_layer.name()}')
print(f'Layer valid: {line_layer.isValid()}')
print(f'Layer feature count: {line_layer.featureCount()}')

# Check if the layer is valid
if not line_layer.isValid():
    print(f'Error: Line layer is not valid or not fully loaded. Path: {geojson_path}')
else:
    print('Line layer is valid.')

    # Start editing the new layer
    line_layer.startEditing()    # Iterate through features in the original layer
    for feature in line_layer.getFeatures():
        # Get the geometry of the feature
        geometry = feature.geometry()
        print(geometry.type())
        # If it's a single line, process it directly
        process_line(geometry.asPolyline(), feature.attributes(), line_layer, threshold_length)
        print('processing linestring')

    # Commit the changes in the new layer
    line_layer.commitChanges()

# Refresh the map canvas
iface.mapCanvas().refresh()

def process_line(line, attributes, layer, threshold_length):
    # Get the length of the line
    length = QgsGeometry.fromPolyline(line).length()
    print(length)

    # Check if the length exceeds the threshold
    if length > threshold_length:
        # Split the line at regular intervals (e.g., every 50 meters)
        step_size = 50
        for distance in range(0, int(length), step_size):
            # Get the point at the specified distance along the line
            point = QgsGeometry.fromPolyline(line).interpolate(distance)

            # Create a new feature with the point geometry
            new_feature = QgsFeature()
            new_feature.setGeometry(QgsGeometry.fromPoint(point))
            new_feature.setAttributes(attributes)

            # Add the new feature to the new line layer
            layer.addFeature(new_feature)
    else:
        # If the length is below the threshold, add the original feature to the new line layer
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPolyline(line))
        new_feature.setAttributes(attributes)
        layer.addFeature(new_feature)
