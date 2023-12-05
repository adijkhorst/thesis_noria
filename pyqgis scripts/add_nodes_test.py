from math import *
import numpy as np
import shutil

MAX_DIST_NODES = 100

original_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_fewnodes.geojson"
new_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_allnodes.geojson"

shutil.copy(original_layer_path, new_layer_path)
# # Add the original layer as a variable (will not be edited)
# original_layer = QgsVectorLayer(original_layer_path, "OriginalLayer", "ogr")
# # QgsProject.instance().addMapLayer(original_layer, False)

# # Create a new layer from the same source (do not edit yet)
# unused_layer = QgsVectorLayer(original_layer.source(), "UnusedLayer", "ogr")
# # QgsProject.instance().addMapLayer(unused_layer)

# # Save the new layer to a new GeoJSON file with a different name (create a copy)
# options = QgsVectorFileWriter.SaveVectorOptions()
# options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
# options.layerOptions = ["PRECISION=NO"]
# QgsVectorFileWriter.writeAsVectorFormatV2(unused_layer, new_layer_path, QgsCoordinateTransformContext(), options)

# Remove the unused layer from the project
# QgsProject.instance().removeMapLayer(unused_layer)

# Create a new layer for modifications (load the new layer again from the new GeoJSON file)
# line_layer = iface.addVectorLayer(new_layer_path, "NewLayer", "ogr")
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

line_layer.startEditing()
layer_provider = line_layer.dataProvider()
layer_provider.addAttributes([QgsField("angle", QVariant.Double)])
line_layer.commitChanges()
line_layer.startEditing()
attr_id = line_layer.attributeList()[-1]
print(attr_id)

features = line_layer.getFeatures()

for feature in features:
    geom = feature.geometry()
    print(geom)
    f_id = feature.id()
    vertices = geom.asPolyline()
    # print(vertices)
    # vertices_array = [[vertex.x(), vertex.y()] for vertex in vertices]
    
    segment_length = geom.length()
    if segment_length == 0:
        line_layer.deleteFeatures([f_id])
        # print(segment_length)
    else:
        angle = vertices[1].azimuth(vertices[0]) #% 180 #to make sure all lines are defined in the same way (clockwise angle with north)
        # if angle > 0:
            # nodes = geom.asPolyline()
            # print(nodes)
            # nodes.reverse()
            # print(nodes)
            # newgeom = QgsGeometry.fromPolylineXY(nodes)
            # print(newgeom)
            # line_layer.changeGeometry(f_id, newgeom)
            # # line_layer.commitChanges()
            # print(feature.geometry())
        # print(angle)
        # attr_value = {attr_id:angle}
        line_layer.changeAttributeValue(f_id, attr_id, angle)
        # print("begin point = ", vertices[0].x(), vertices[0].y())
        # print("end point = ", vertices[1].x(), vertices[1].y())
        # print("distance = ", segment_length)
        if segment_length > MAX_DIST_NODES:
            extra_nodes = segment_length//MAX_DIST_NODES
            interpolation_distance = segment_length / (extra_nodes + 1)
            for i in range(int(extra_nodes)):
                # print(geom.interpolate(interpolation_distance))
                interpolated_point = geom.interpolate(interpolation_distance*(i+1)).asPoint()
                geom.insertVertex(x = interpolated_point.x(), y = interpolated_point.y(), beforeVertex = i+1)
                # print("interpolated point at = ", interpolated_point.x(), interpolated_point.y())\
            line_layer.changeGeometry(f_id, geom)
    # check if vertices were actually inserted
    # print(geom.type())
    #     print(vertex.x(), vertex.y())

# Save the new layer to a new GeoJSON file
options = QgsVectorFileWriter.SaveVectorOptions()
options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
options.layerOptions = ["PRECISION=NO"]
QgsVectorFileWriter.writeAsVectorFormatV2(line_layer, new_layer_path, QgsCoordinateTransformContext(), options)

    # print(len(vertices), str(angles))
line_layer.commitChanges()
line_layer.endEditCommand()
iface.mapCanvas().refresh()
