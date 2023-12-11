from math import *
import numpy as np
import networkx as nx

import sys
sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")
import network_creation

### Create a copy of original file under new name to edit new file instead of old file
original_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_directed_exploded.geojson"

# Load layer that will be edited
line_layer = QgsVectorLayer(original_layer_path, "NewLayer", "ogr")
QgsProject.instance().addMapLayer(line_layer)

# Print layer information for debugging
print(f'Layer name: {line_layer.name()}')
print(f'Layer valid: {line_layer.isValid()}')
print(f'Layer feature count: {line_layer.featureCount()}')

# Check if the layer is valid
if not line_layer.isValid():
    print(f'Error: Line layer is not valid or not fully loaded. Path: {new_layer_path}')
else:
    print('Line layer is valid.')
    
### if there is no field for start and end point

### if there is no field called transition probabilities, then add it
last_id = line_layer.attributeList()[-1]
if not line_layer.attributeDisplayName(last_id) == 'transition_probability':
    line_layer.startEditing()
    layer_provider = line_layer.dataProvider()
    layer_provider.addAttributes([QgsField("transition_probability", QVariant.Double)])
    line_layer.commitChanges()
    print("Added attribute field for transition probability.")


line_layer.startEditing()
start_id = line_layer.attributeList()[-3]
end_id = line_layer.attributeList()[-2]
prob_id = line_layer.attributeList()[-1]

G = network_creation.create_network()

for feature in line_layer.getFeatures():
    geom = feature.geometry().asPolyline()
    start_node = (geom[0].x(), geom[0].y())
    end_node = (geom[1].x(), geom[1].y())
    if G.has_edge(start_node, end_node):
        prob = round(G[start_node][end_node]['transition_probability'], 3)
        line_layer.changeAttributeValue(feature.id(), prob_id, float(prob))
    else:
        print("G does not have edge: ", start_node, end_node)
    

# Save the new layer to the GeoJSON file
options = QgsVectorFileWriter.SaveVectorOptions()
options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
options.layerOptions = ["PRECISION=NO"]
QgsVectorFileWriter.writeAsVectorFormatV2(line_layer, original_layer_path, QgsCoordinateTransformContext(), options)

# Refresh map
line_layer.commitChanges()
line_layer.endEditCommand()
iface.mapCanvas().refresh()