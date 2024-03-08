import numpy as np
# from qgis.core import QgsVectorLayer

import sys
sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/pyqgis scripts")
import display_probabilities
sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")
import network_creation
import wind_data

RADIUS_SHORE_IMPACT = 50 #adjust later such that this is MAX_DIST_NODES/2

shore_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/shore_types_delft_reprojected.geojson"
shore_layer = QgsVectorLayer(shore_layer_path, '', "ogr")

water_vegetation_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/water_vegetation_delft.geojson"
water_vegetation_layer = QgsVectorLayer(water_vegetation_path, '', "ogr")

corners_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/sharp_corners_delft.geojson"
corners_layer = QgsVectorLayer(corners_layer_path, '', "ogr")

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
# if not nodes_layer.attributeDisplayName(nodes_layer.attributeList()[-1]) == 'stuck_probability':    
#     layer_provider = nodes_layer.dataProvider()
#     layer_provider.addAttributes([QgsField('stuck_probability', QVariant.Double)])
#     nodes_layer.commitChanges()
#     print("Added field for probability of getting stuck")
layer_provider = nodes_layer.dataProvider()
layer_provider.addAttributes([QgsField('dead_ends', QVariant.Double), QgsField('sharp_corners', QVariant.Double), \
                            QgsField('shore_boats', QVariant.Double), QgsField('shore_vegetation', QVariant.Double), \
                            QgsField('water_vegetation', QVariant.Double), QgsField('stuck_probability', QVariant.Double)])
nodes_layer.commitChanges()


name_list = [field.name() for field in nodes_layer.fields()]
dead_end_id = name_list.index("dead_ends")
sharp_corners_id = name_list.index("sharp_corners") 
shore_boats_id = name_list.index("shore_boats")
shore_veg_id = name_list.index("shore_vegetation")
water_veg_id = name_list.index("water_vegetation")
stuck_prob_id = name_list.index("stuck_probability")

attr_id = nodes_layer.attributeList()[-1]

G = network_creation.create_network()

### for every node in stuck layer, check if the shores surrounding it with nodesdistance/2 have reasons why plastic should get stuck
# i = 0

index = QgsSpatialIndex(water_vegetation_layer.getFeatures())

nodes_layer.startEditing()
for feature in nodes_layer.getFeatures():
    #check if it is a dead end
    position = (feature.geometry().asPoint().x(), feature.geometry().asPoint().y())
    if sum(1 for _ in G.successors(position)) == 1:
        for x in G.predecessors(position):
            forward_prob = G[x][position]['transition_probability']
        for x in G.successors(position):
            G[position][x]['transition_probability'] = 1-forward_prob*0.5
        dead_ends_prob = 0.5*forward_prob
    else:
        dead_ends_prob = 0
        
    
    geom_buffer = feature.geometry().buffer(RADIUS_SHORE_IMPACT, -1)
    #check close sharp corners
    close_sharp_corners = np.array([feat['wind_prob'] for feat in corners_layer.getFeatures() if (feat.geometry().intersects(geom_buffer) and feat['sharp']==1)])
    sharp_corners_prob = 1-np.prod(1-0.5*close_sharp_corners)
    
    #check if shore types close to node are reasons to get stuck (houseboats or vegetation)
    close_shore_features = [feat for feat in shore_layer.getFeatures() if feat.geometry().intersects(geom_buffer)]
    for feat in close_shore_features:
        # if feat['type'] == 'houseboat': #add mooring spots later
        #     shore_boats_prob = 0.3
        # else:
        #     shore_boats_prob = 0
        shore_boats_prob = 0.3 if feat['type'] == 'houseboat' else 0
        shore_veg_prob = 0.3 if feat['type'] == 'vegetation' else 0
        # ALSO ADD MOORING SPOTS FOR TEMPORARY BOATS
        
    
    #check if water vegetation
    water_veg_prob = 0.45 if len(index.intersects(feature.geometry().boundingBox()))>0 else 0
        
    
    stuck_prob = 1 - np.prod(1-np.array([dead_ends_prob, sharp_corners_prob, shore_boats_prob, shore_veg_prob, water_veg_prob]))
    nodes_layer.changeAttributeValues(feature.id(), {dead_end_id: float(dead_ends_prob), sharp_corners_id: float(sharp_corners_prob), shore_boats_id: shore_boats_prob, \
                                    shore_veg_id: shore_veg_prob, water_veg_id: water_veg_prob, stuck_prob_id: float(stuck_prob)})
    
nodes_layer.commitChanges()
nodes_layer.endEditCommand()
iface.mapCanvas().refresh()

# display_probabilities.display_probabilities_map(G)

        
    

