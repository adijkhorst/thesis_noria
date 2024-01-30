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
    
    #first check if it is a dead end
    position = (feature.geometry().asPoint().x(), feature.geometry().asPoint().y())
    if sum(1 for _ in G.successors(position)) == 1:
        for x in G.predecessors(position):
            prob = G[x][position]['transition_probability']
        for x in G.successors(position):
            G[position][x]['transition_probability'] = 1-prob
    
    #then check if shore types close to node are reasons to get stuck (houseboats or vegetation)
    geom_buffer = feature.geometry().buffer(RADIUS_SHORE_IMPACT, -1)
    close_shore_features = [feat for feat in shore_layer.getFeatures() if feat.geometry().intersects(geom_buffer)]
    for feat in close_shore_features:
        if feat['type'] == ('houseboat' or 'vegetation'): #add mooring spots later
            if prob < 0.4:
                prob = 0.4
    
    #then check sharp corners + wind directions
    
    wind_directions = wind_data.get_wind_directions()
    close_sharp_corners = [[feat['wind_range_min'], feat['wind_range_max']] for feat in corners_layer.getFeatures() if (feat.geometry().intersects(geom_buffer) and feat['sharp']==1)]
    # print(close_sharp_corners)
    
    if len(close_sharp_corners) > 0:
        days = len(wind_directions)*[False]
        for corner in close_sharp_corners:
            if corner[0] < corner[1]:
                booleans = (wind_directions > corner[0]) & (wind_directions < corner[1])
            else:
                booleans = (wind_directions > corner[0]) | (wind_directions < corner[1])
            days = np.any([days, booleans], axis = 0)
        wind_prob = len(wind_directions[days])/len(wind_directions)
        if prob < wind_prob:
            prob = wind_prob
            
    prob = round(prob, 3)
    nodes_layer.changeAttributeValue(feature.id(), attr_id, float(prob))
    # print(feature['stuck_probability'])
    # i += 1
    # if i == 9:
    #     break
    
nodes_layer.commitChanges()
nodes_layer.endEditCommand()
iface.mapCanvas().refresh()

# display_probabilities.display_probabilities_map(G)

        
    

