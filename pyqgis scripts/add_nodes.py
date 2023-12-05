from math import *
import numpy as np
import shutil

MAX_DIST_NODES = 100

### Create a copy of original file under new name to edit new file instead of old file
original_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_fewnodes.geojson"
new_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_allnodes.geojson"
shutil.copy(original_layer_path, new_layer_path) 

# Load layer that will be edited
line_layer = QgsVectorLayer(new_layer_path, "NewLayer", "ogr")
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

### Add extra field for angle of segment
line_layer.startEditing()
layer_provider = line_layer.dataProvider()
layer_provider.addAttributes([QgsField("angle", QVariant.Double)])
line_layer.commitChanges()


line_layer.startEditing()
attr_id = line_layer.attributeList()[-1]
# print(attr_id)

# features = line_layer.getFeatures()
for feature in line_layer.getFeatures():
    geom = feature.geometry()
    segment_length = geom.length()
    ### remove zero length segments, interpolate vertices for segments that are too long
    if segment_length == 0:
        line_layer.deleteFeatures([feature.id()])
    else:
        vertices = geom.asPolyline()
        angle = vertices[1].azimuth(vertices[0])
        if angle > 0: #turn segment around such that all edges are oriented to the right
            vertices.reverse()
            geom = QgsGeometry.fromPolylineXY(vertices)
            line_layer.changeGeometry(feature.id(), geom)
        line_layer.changeAttributeValue(feature.id(), attr_id, angle)
        
        ### interpolate equal distances if segment is larger than threshold
        if segment_length > MAX_DIST_NODES:
            extra_nodes = segment_length//MAX_DIST_NODES
            interpolation_distance = segment_length / (extra_nodes + 1)
            for i in range(int(extra_nodes)):
                interpolated_point = geom.interpolate(interpolation_distance*(i+1)).asPoint()
                geom.insertVertex(x = interpolated_point.x(), y = interpolated_point.y(), beforeVertex = i+1)
            line_layer.changeGeometry(feature.id(), geom)

# Save the new layer to a new GeoJSON file
options = QgsVectorFileWriter.SaveVectorOptions()
options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
options.layerOptions = ["PRECISION=NO"]
QgsVectorFileWriter.writeAsVectorFormatV2(line_layer, new_layer_path, QgsCoordinateTransformContext(), options)

# Refresh map
line_layer.commitChanges()
line_layer.endEditCommand()
iface.mapCanvas().refresh()
