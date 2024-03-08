from math import *
import numpy as np
import processing

MAX_CANAL_WIDTH = 100

### first create point layer with nodes that will get canal_width attribute
line_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_directed_exploded.geojson"
nodes_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/catching_probabilities.geojson"
nodes_layer = processing.run("native:extractvertices", {'INPUT': line_layer_path,
               'OUTPUT': 'TEMPORARY_OUTPUT'})["OUTPUT"]
nodes_layer = processing.run("native:deleteduplicategeometries", {'INPUT': nodes_layer,
                'OUTPUT': nodes_layer_path})

# nodes_layer = iface.addVectorLayer(nodes_layer_path, "catching_probabilities", "ogr")

new_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/catching_probabilities.geojson"
polygon_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Static model/Static Model Delft/Static model/waterpolygon_delft.geojson"
test_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/testlayer_canalwidth.geojson"

# Add the polygon layer as a variable (will not be edited)
polygon_layer = QgsVectorLayer(polygon_layer_path, '', "ogr")

# Create empty test layer to show the clipped line segments
test_layer = QgsVectorLayer("Linestring?crs=EPSG:28992","TestLayer","memory")
# QgsProject.instance().addMapLayer(test_layer)

# Add schie layer to check max boat width
schie_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/schie_nodes.geojson"
schie_layer = QgsVectorLayer(schie_layer_path, '', "ogr")

# Create node layer to edit canal width
new_layer = QgsVectorLayer(new_layer_path, 'catching_probabilities', "ogr")
QgsProject.instance().addMapLayer(new_layer)

# Print layer information for debugging
print(f'Layer name: {new_layer.name()}')
print(f'Layer valid: {new_layer.isValid()}')
print(f'Layer feature count: {new_layer.featureCount()}')

# Check if the layer is valid
if not new_layer.isValid() or not test_layer.isValid() or not polygon_layer.isValid():
    print(f'Error: Line layer is not valid or not fully loaded. (Check which one) Path: {new_layer_path}')
else:
    print('Line layer is valid.')
    
### Add new field called canal width if field does not exist yet
name_list = [field.name() for field in new_layer.fields()]
if not 'canal_width' in name_list: 
    new_layer.startEditing()
    layer_provider = new_layer.dataProvider()
    layer_provider.addAttributes([QgsField("canal_width", QVariant.Double)])
    new_layer.commitChanges()
    print("Added attribute field for canal width.")
if not 'catching_probability' in name_list: 
    new_layer.startEditing()
    layer_provider = new_layer.dataProvider()
    layer_provider.addAttributes([QgsField("catching_probability", QVariant.Double)])
    new_layer.commitChanges()
    print("Added attribute field for catching probability.")

test_layer.startEditing()
layer_provider = test_layer.dataProvider()
layer_provider.addAttributes(new_layer.fields())
test_layer.commitChanges()


name_list = [field.name() for field in new_layer.fields()]
width_id = name_list.index("canal_width")
catching_prob_id = name_list.index("catching_probability")

index = QgsSpatialIndex(schie_layer.getFeatures())

new_layer.startEditing()
test_layer.startEditing()
for feature in new_layer.getFeatures():
    point = feature.geometry().asPoint()
    angle = feature['angle'] + 90
    unit_vector = [np.sin(angle/180*np.pi), np.cos(angle/180*np.pi)]
    new_vertices = [QgsPoint(point.x()+MAX_CANAL_WIDTH/2 * unit_vector[0], point.y()+MAX_CANAL_WIDTH/2 * unit_vector[1]), QgsPoint(point.x()-MAX_CANAL_WIDTH/2 * unit_vector[0], point.y()-MAX_CANAL_WIDTH/2 * unit_vector[1])]
    new_feature = QgsFeature()
    new_feature.setGeometry(QgsGeometry.fromPolyline(new_vertices))
    new_feature.setAttributes(feature.attributes())#[:len(test_layer.attributeList())])
    test_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
    test_layer = processing.run("native:clip", {'INPUT': test_layer,
               'OVERLAY': polygon_layer_path,
               'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT})['OUTPUT']
    test_layer.startEditing()
    for test_feature in test_layer.getFeatures(): # there should be only 1 feature!
        length = test_feature.geometry().length()
        test_layer.deleteFeature(test_feature.id())
        new_layer.changeAttributeValue(feature.id(), width_id, length)
        
        if len(index.intersects(feature.geometry().boundingBox()))>0:
            catching_prob = (length - 21)/length
        else:
            catching_prob = (length - 4)/length
        
        if catching_prob > 0:
            new_layer.changeAttributeValue(feature.id(), catching_prob_id, catching_prob)
        else:
            new_layer.changeAttributeValue(feature.id(), catching_prob_id, 0) #set to zero when boats seem larger than canal width

test_layer.updateExtents()
test_layer.commitChanges()
test_layer.endEditCommand()

new_layer.commitChanges()
new_layer.endEditCommand()

# QgsProject.instance().addMapLayer(test_layer)
iface.mapCanvas().refresh()
