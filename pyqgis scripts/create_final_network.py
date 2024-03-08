### input: geojson with simplified waterlines
### output: layer with extra nodes and edges for directed network
## new attribute: angle of water segment

from math import *
import numpy as np
import shutil

MAX_DIST_NODES = 60


original_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_fewnodes.geojson"
new_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/delft_final_network.geojson"

shutil.copy(original_layer_path, new_layer_path)
line_layer = QgsVectorLayer(new_layer_path, "final_network_layer", "ogr")
QgsProject.instance().addMapLayer(line_layer)

def add_nodes(line_layer):
    line_layer.startEditing()
    layer_provider = line_layer.dataProvider()
    layer_provider.addAttributes([QgsField("angle", QVariant.Double)])
    line_layer.commitChanges()
    
    name_list = [field.name() for field in line_layer.fields()]
    angle_id = name_list.index("angle")
    
    line_layer.startEditing()
    for feature in line_layer.getFeatures():
        geom = feature.geometry()
        segment_length = geom.length()
        ### remove zero length segments, interpolate vertices for segments that are too long
        if segment_length == 0:
            line_layer.deleteFeatures([feature.id()])
        else:
            vertices = geom.asPolyline()
            angle = vertices[0].azimuth(vertices[1])
            if angle < 0: #turn segment around such that all edges are oriented to the right
                vertices.reverse()
                geom = QgsGeometry.fromPolylineXY(vertices)
                line_layer.changeGeometry(feature.id(), geom)
                angle = vertices[0].azimuth(vertices[1])
            line_layer.changeAttributeValue(feature.id(), angle_id, angle)
            
            ### interpolate equal distances if segment is larger than threshold
            if segment_length > MAX_DIST_NODES:
                extra_nodes = segment_length//MAX_DIST_NODES
                interpolation_distance = segment_length / (extra_nodes + 1)
                for i in range(int(extra_nodes)):
                    interpolated_point = geom.interpolate(interpolation_distance*(i+1)).asPoint()
                    geom.insertVertex(x = interpolated_point.x(), y = interpolated_point.y(), beforeVertex = i+1)
                line_layer.changeGeometry(feature.id(), geom)
                
    line_layer.commitChanges()
    line_layer.endEditCommand()
    iface.mapCanvas().refresh()

def make_directed(line_layer):
    name_list = [field.name() for field in line_layer.fields()]
    angle_id = name_list.index("angle")
    
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
            old_angle = new_feature[angle_id]
            new_feature.setAttribute(angle_id, old_angle-180)
            line_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
            
            
            ### part 2: add cross edges
            new_vertices.reverse() # reverse back so indices for extra edges are correct
            for i in range(len(new_vertices)-2): #-3 because we don't need cross edges for the first and last node 
                cross_vertices1 = [new_vertices[i+1], existing_vertices[i+2]]
                cross_vertices2 = [existing_vertices[i+1], new_vertices[i]]
                cross_edge1 = QgsFeature()
                cross_edge2 = QgsFeature()
                cross_edge1.setGeometry(QgsGeometry.fromPolyline(cross_vertices1))
                cross_edge2.setGeometry(QgsGeometry.fromPolyline(cross_vertices2))
                cross_edge1.setAttributes(feature.attributes())
                cross_edge2.setAttributes(feature.attributes())
                old_angle = cross_edge2[angle_id]
                cross_edge2.setAttribute(angle_id, old_angle-180)
                line_layer.addFeature(cross_edge1, QgsFeatureSink.FastInsert)
                line_layer.addFeature(cross_edge2, QgsFeatureSink.FastInsert)
        elif len(existing_vertices) == 2:
            # add edge in opposite direction, no extra nodes
            new_vertices = existing_vertices
            new_vertices.reverse()
            new_feature = QgsFeature()
            new_feature.setGeometry(QgsGeometry.fromPolyline(new_vertices))
            new_feature.setAttributes(feature.attributes())
            old_angle = new_feature[angle_id]
            new_feature.setAttribute(angle_id, old_angle-180)
            line_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
    line_layer.updateExtents()

    line_layer.commitChanges()
    line_layer.endEditCommand()
    iface.mapCanvas().refresh()
    
add_nodes(line_layer)
make_directed(line_layer)