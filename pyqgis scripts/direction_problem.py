from math import *
import numpy as np
import shutil

original_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_allnodes.geojson"
new_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_directed_doublenodes.geojson"
shutil.copy(original_layer_path, new_layer_path)

# Create a new layer for modifications (load the new layer again from the new GeoJSON file)
line_layer = iface.addVectorLayer(new_layer_path, "NewLayer", "ogr")

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
# layer_provider = line_layer.dataProvider()
# layer_provider.addAttributes([QgsField("oldnew", QVariant.String)])
# for feature in line_layer.getFeatures():
    
# line_layer.commitChanges()
line_layer.startEditing()

for feature in line_layer.getFeatures():
    existing_vertices = [vertex for vertex in feature.geometry().vertices()]
    if len(existing_vertices) > 2:
        angle = feature.attributes()[-1] % 180 + 90
        unit_vector = [np.sin(angle/180*np.pi), np.cos(angle/180*np.pi)]
        new_vertices = [existing_vertices[0]]
        
        for existing_vertex in existing_vertices[1:-1]:
            new_vertex = QgsPoint(existing_vertex.x()+3*unit_vector[0], existing_vertex.y()+3*unit_vector[1])
            new_vertices += [new_vertex]
        new_vertices += [existing_vertices[-1]]
        new_vertices.reverse() #flip list so orientation of edges is opposite
        
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPolyline(new_vertices))
        new_feature.setAttributes(feature.attributes())
        
        # print("Old: ", [vertex for vertex in feature.geometry().vertices()])
        # print("New: ", [vertex for vertex in new_feature.geometry().vertices()])
        
        # print(new_feature.geometry())
        # (res, outFeats) = line_layer.dataProvider().addFeatures([new_feature])
        # layer_provider.addFeature(new_feature, QgsFeatureSink.FastInsert)
        line_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
        
        ### part 2: add cross edges
        new_vertices.reverse() # reverse back so indices for extra edges are correct
        for i in range(len(new_vertices)-3): #-3 because we don't need cross edges for the first and last node 
            cross_vertices1 = [new_vertices[i+1], existing_vertices[i+2]]
            cross_vertices2 = [existing_vertices[i+2], new_vertices[i+1]]
            cross_edge1 = QgsFeature()
            cross_edge2 = QgsFeature()
            cross_edge1.setGeometry(QgsGeometry.fromPolyline(cross_vertices1))
            cross_edge2.setGeometry(QgsGeometry.fromPolyline(cross_vertices2))
            cross_edge1.setAttributes(feature.attributes())
            cross_edge2.setAttributes(feature.attributes())
            line_layer.addFeature(cross_edge1, QgsFeatureSink.FastInsert)
            line_layer.addFeature(cross_edge2, QgsFeatureSink.FastInsert)
    elif len(existing_vertices) == 2:
        # add edge in opposite direction, no extra nodes
        new_vertices = existing_vertices
        new_vertices.reverse()
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPolyline(new_vertices))
        new_feature.setAttributes(feature.attributes())
        print("Old: ", [vertex for vertex in feature.geometry().vertices()])
        print("New: ", [vertex for vertex in new_feature.geometry().vertices()])
        line_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)


line_layer.updateExtents()

line_layer.commitChanges()
line_layer.endEditCommand()
iface.mapCanvas().refresh()
# iface.zoomToActiveLayer()

    
