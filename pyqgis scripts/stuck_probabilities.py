import numpy as np

import sys
sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")
import network_creation

RADIUS_SHORE_IMPACT = 50 #adjust later such that this is MAX_DIST_NODES/2

shore_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/shore_types_delft_reprojected.geojson"
shore_layer = QgsVectorLayer(shore_layer_path, '', "ogr")

### first create point layer with nodes that will get init_distribution attribute
line_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_directed_exploded.geojson"
nodes_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/stuck_probabilities.geojson"

nodes_layer = processing.run("native:extractvertices", {'INPUT': line_layer_path,
               'OUTPUT': 'TEMPORARY_OUTPUT'})["OUTPUT"]
nodes_layer = processing.run("native:deleteduplicategeometries", {'INPUT': nodes_layer,
                'OUTPUT': nodes_layer_path})
                

nodes_layer = QgsVectorLayer(nodes_layer_path, 'stuck_probabilities', "ogr")
QgsProject.instance().addMapLayer(nodes_layer)
nodes_layer.startEditing()
### if there is no field called stuck_probability, then add it
if not nodes_layer.attributeDisplayName(nodes_layer.attributeList()[-1]) == 'stuck_probability':    
    layer_provider = nodes_layer.dataProvider()
    layer_provider.addAttributes([QgsField('stuck_probability', QVariant.Double)])
    nodes_layer.commitChanges()
    print("Added field for probability of getting stuck")
attr_id = nodes_layer.attributeList()[-1]

G = network_creation.create_network()

### for every node in stuck layer, check if the shores surrounding it with nodesdistance/2 have reasons why plastic should get stuck
# i = 0
nodes_layer.startEditing()
for feature in nodes_layer.getFeatures():
    prob = 0
    
    position = (feature.geometry().asPoint().x(), feature.geometry().asPoint().y())
    if sum(1 for _ in G.successors(position)) == 1:
        for x in G.predecessors(position):
            prob = G[x][position]['transition_probability']
        for x in G.successors(position):
            G[position][x]['transition_probability'] = 1-prob
        nodes_layer.changeAttributeValue(feature.id(), attr_id, float(prob))
        print(feature['stuck_probability'])
nodes_layer.commitChanges()
nodes_layer.endEditCommand()
iface.mapCanvas().refresh()

    
    # # nodes_layer.changeAttributeValue(feature.id(), attr_id, NULL)
    # geom_buffer = feature.geometry().buffer(RADIUS_SHORE_IMPACT, -1)
    # close_shore_features = [feat for feat in shore_layer.getFeatures() if feat.geometry().intersects(geom_buffer)]
    
    
    # ### if there are certain shoretypes close, then change probability of getting stuck
    # # order should be from low to high probability
    # for feat in close_shore_features:
    #     print(feat['type'])
    #     if feat['type'] == ('houseboat' or 'vegetation'):
    #         prob = 0.4
    # print(prob)
    
    # i += 1
    # if i == 10:
    #     break

display_probabilities_map(G)

        
    

