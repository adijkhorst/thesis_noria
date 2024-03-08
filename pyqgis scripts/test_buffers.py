import numpy as np
# from qgis.core import QgsVectorLayer

RADIUS_SHORE_IMPACT = 50 #adjust later such that this is MAX_DIST_NODES/2

nodes_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/test_buffers.geojson"
nodes_layer = QgsVectorLayer(nodes_layer_path, '', "ogr")

shore_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/shore_types_delft_reprojected.geojson"
shore_layer = QgsVectorLayer(shore_layer_path, '', "ogr")

test_layer = QgsVectorLayer("Polygon?crs=EPSG:28992","TestLayer","memory")
QgsProject.instance().addMapLayer(test_layer)

# QgsProject.instance().addMapLayer(nodes_layer)
nodes_layer.startEditing()

### for every node in stuck layer, check if the shores surrounding it with nodesdistance/2 have reasons why plastic should get stuck
# i = 0
test_layer.startEditing()
for feature in nodes_layer.getFeatures():
    
    #then check if shore types close to node are reasons to get stuck (houseboats or vegetation)
    geom_buffer = feature.geometry().buffer(RADIUS_SHORE_IMPACT/2, 9)
    close_shore_features = [feat for feat in shore_layer.getFeatures() if feat.geometry().intersects(geom_buffer)]

    new_feature = QgsFeature()
    new_feature.setGeometry(geom_buffer)
    new_feature.setAttributes([])#[:len(test_layer.attributeList())])
    test_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
    
    
test_layer.commitChanges()
test_layer.endEditCommand()
iface.mapCanvas().refresh()



