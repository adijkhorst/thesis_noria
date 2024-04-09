### input: final layer of directed network
### output: vector initial distribution, transition matrix including probability of getting stuck, proportion of waterway that can be blocked (betas)

# also display transition probabilities, getting stuck, init distr, betas
import numpy as np
import networkx as nx
import geopandas as gpd

import sys
sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")
import wind_data

layers_folder = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/"

RADIUS_SOURCES_IMPACT = 100

def create_nodes_layer(final_network_layer_path, nodes_attributes_layer_path):
    nodes_attributes_layer = processing.run("native:extractvertices", {'INPUT': final_network_layer_path,
               'OUTPUT': 'TEMPORARY_OUTPUT'})["OUTPUT"]
    nodes_attributes_layer = processing.run("native:deleteduplicategeometries", {'INPUT': nodes_attributes_layer,
                'OUTPUT': nodes_attributes_layer_path})
    
    nodes_attributes_layer = iface.addVectorLayer(nodes_attributes_layer_path, "nodes_attributes", "ogr")
    
    # ### add fields for initial probabilities, stuck probabilities and catching probabilities
    # nodes_attributes_layer.startEditing()
    # layer_provider = nodes_attributes_layer.dataProvider()
    # layer_provider.addAttributes([QgsField('init_probability', QVariant.Double), QgsField('max_boat_width', QVariant.Double),
    #                         QgsField('canal_width', QVariant.Double), QgsField('catching_probability', QVariant.Double),
    #                         QgsField('dead_ends', QVariant.Double), QgsField('sharp_corners', QVariant.Double), \
    #                         QgsField('shore_boats', QVariant.Double), QgsField('shore_vegetation', QVariant.Double), \
    #                         QgsField('water_vegetation', QVariant.Double), QgsField('stuck_probability', QVariant.Double)])
    # nodes_attributes_layer.commitChanges()
    
    # init_prob_id, stuck_prob_id, catch_prob_id = nodes_attributes_layer.attributeList()[-3], nodes_attributes_layer.attributeList()[-2], nodes_attributes_layer.attributeList()[-1]
    
    return nodes_attributes_layer
    
    
def initial_probabilities(nodes_layer, sources_layer_path, radius_impact):
    sources_layer = QgsVectorLayer(sources_layer_path, '', "ogr") #will not be edited
    
    nodes_layer.startEditing()

    ### if there is no field called init probability, then add it
    if not nodes_layer.attributeDisplayName(nodes_layer.attributeList()[-1]) == 'init_probability':    
        layer_provider = nodes_layer.dataProvider()
        layer_provider.addAttributes([QgsField('init_probability', QVariant.Double)])
        nodes_layer.commitChanges()
        print("Added attribute field for initial probability")

    attr_id = nodes_layer.attributeList()[-1]

    total = 0
    nodes_layer.startEditing()
    for feature in nodes_layer.getFeatures():
        geom_buffer = feature.geometry().buffer(radius_impact, 10)
        close_sources = [feat for feat in sources_layer.getFeatures() if feat.geometry().intersects(geom_buffer)]
        num_sources = len(close_sources)
        total += num_sources
        nodes_layer.changeAttributeValue(feature.id(), attr_id, num_sources)

    for feature in nodes_layer.getFeatures():
        prob = feature['init_probability']/total
        nodes_layer.changeAttributeValue(feature.id(), attr_id, float(prob))

    nodes_layer.commitChanges()
    nodes_layer.endEditCommand()
    iface.mapCanvas().refresh()


def create_network(final_network_layer_path):
    # Read shapefile
    gdf = gpd.read_file(final_network_layer_path)

    # Create a new NetworkX graph
    G = nx.DiGraph()

    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        line = row['geometry']
        angle = row['angle']

        # Extract the coordinates of the LineString
        coordinates = list(line.coords)
    
        # Add nodes to the graph
        for coord in coordinates:
            G.add_node(coord)
    
        # Add edges to the graph
        for i in range(1, len(coordinates)):
            node_from = coordinates[i - 1]
            node_to = coordinates[i]
            G.add_edge(node_from, node_to, weight = angle)
    
    # G.remove_edges_from(nx.selfloop_edges(G))
    attrs = {}
    for index, node in enumerate(G.nodes()):
        attrs[node] = {'label': index+1, 'position' : node}
    nx.set_node_attributes(G, attrs)
    
    return G
    
    
def get_transition_probabilities(G):
    ### Calculate transition probabilities and put as attribute on edges
    attrs = {}
    wind_directions = wind_data.get_wind_directions(2022)
    for node in G.nodes():
        neighbors = [neighbor for neighbor in G.neighbors(node)]
        num_neighbors = len(neighbors)
        transition_probabilities = np.zeros(num_neighbors)
        edge_angles = [G[node][neighbor]["weight"] % 360 for neighbor in neighbors]
    
        threshold = 10 #if less than 5 degrees from bisector angle
    
        for direction in wind_directions:
            difference = np.min([360-np.abs(edge_angles - direction), np.abs(edge_angles - direction)], axis = 0)
            index, value = np.argmin(difference), np.min(difference)
            difference[index] += 360
            second_index, second_value = np.argmin(difference), np.min(difference)
            transition_probabilities[index] += 1
            if second_value - value < threshold:
                transition_probabilities[second_index] += 1
    
        transition_probabilities /= np.sum(transition_probabilities)
        for index, neighbor in enumerate(neighbors):
            attrs[(node, neighbor)] = {"transition_probability": transition_probabilities[index]}
    
    nx.set_edge_attributes(G, attrs)
    
    return G

def display_probabilities_map(G, line_layer):
    ### if there is no field called transition probabilities, then add it
    last_id = line_layer.attributeList()[-1]
    if not line_layer.attributeDisplayName(last_id) == 'transition_probability':
        line_layer.startEditing()
        layer_provider = line_layer.dataProvider()
        layer_provider.addAttributes([QgsField("transition_probability", QVariant.Double)])
        line_layer.commitChanges()
        print("Added attribute field for transition probability.")

    line_layer.startEditing()
    prob_id = line_layer.attributeList()[-1]
    for feature in line_layer.getFeatures():
        geom = feature.geometry().asPolyline()
        start_node = (geom[0].x(), geom[0].y())
        end_node = (geom[1].x(), geom[1].y())
        if G.has_edge(start_node, end_node):
            prob = round(G[start_node][end_node]['transition_probability'], 3)
            line_layer.changeAttributeValue(feature.id(), prob_id, float(prob))
        else:
            print("G does not have edge: ", start_node, end_node)
    # Refresh map
    line_layer.commitChanges()
    line_layer.endEditCommand()
    iface.mapCanvas().refresh()

# def nodes_indices(G, nodes_layer):
#     for feature in nodes_layer.getFeatures():
        

def catching_probabilities(nodes_layer, polygon_layer, max_boat_width_layer, MAX_CANAL_WIDTH):
    # Create empty test layer to show the clipped line segments
    test_layer = QgsVectorLayer("Linestring?crs=EPSG:28992","TestLayer","memory")

    # Add schie layer to check max boat width
    # schie_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/schie_nodes.geojson"
    # schie_layer = QgsVectorLayer(schie_layer_path, '', "ogr")


    ### Add new field called canal width if field does not exist yet
    name_list = [field.name() for field in nodes_layer.fields()]
    if not 'max_boat_width' in name_list: 
        nodes_layer.startEditing()
        layer_provider = nodes_layer.dataProvider()
        layer_provider.addAttributes([QgsField("max_boat_width", QVariant.Double)])
        nodes_layer.commitChanges()
        print("Added attribute field for max boat width.")
    if not 'canal_width' in name_list: 
        nodes_layer.startEditing()
        layer_provider = nodes_layer.dataProvider()
        layer_provider.addAttributes([QgsField("canal_width", QVariant.Double)])
        nodes_layer.commitChanges()
        print("Added attribute field for canal width.")
    if not 'catching_probability' in name_list: 
        nodes_layer.startEditing()
        layer_provider = nodes_layer.dataProvider()
        layer_provider.addAttributes([QgsField("catching_probability", QVariant.Double)])
        nodes_layer.commitChanges()
        print("Added attribute field for catching probability.")

    test_layer.startEditing()
    layer_provider = test_layer.dataProvider()
    layer_provider.addAttributes(nodes_layer.fields())
    test_layer.commitChanges()


    name_list = [field.name() for field in nodes_layer.fields()]
    boat_width_id = name_list.index("max_boat_width")
    canal_width_id = name_list.index("canal_width")
    catching_prob_id = name_list.index("catching_probability")

    # index = QgsSpatialIndex(schie_layer.getFeatures())

    nodes_layer.startEditing()
    test_layer.startEditing()
    for feature in nodes_layer.getFeatures():
        point = feature.geometry().asPoint()
        
        #get max boat width from layer
        max_boat_width = 0
        for feat in max_boat_width_layer.getFeatures():
            if feat.geometry().contains(point):
                max_boat_width = feat['max_boat_width']
        nodes_layer.changeAttributeValue(feature.id(), boat_width_id, max_boat_width)
        
        
        #calculate length using line segment clipped
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
        length = 0
        for test_feature in test_layer.getFeatures(): # there should be only 1 feature!
            length = test_feature.geometry().length()
            test_layer.deleteFeature(test_feature.id())
            nodes_layer.changeAttributeValue(feature.id(), canal_width_id, length)
            catching_prob = (length - max_boat_width)/length
            if catching_prob > 0:
                nodes_layer.changeAttributeValue(feature.id(), catching_prob_id, catching_prob)
            else:
                nodes_layer.changeAttributeValue(feature.id(), catching_prob_id, 0) #set to zero when boats seem larger than canal width
        if length == 0: #if there was no feature in test_layer then length is still 0
            nodes_layer.changeAttributeValue(feature.id(), canal_width_id, 0)
            nodes_layer.changeAttributeValue(feature.id(), catching_prob_id, 0)

    test_layer.updateExtents()
    test_layer.commitChanges()
    test_layer.endEditCommand()

    nodes_layer.commitChanges()
    nodes_layer.endEditCommand()
    iface.mapCanvas().refresh()
    
    

def stuck_probabilities(nodes_layer, G, shore_layer_path, MAX_DIST_NODES, water_vegetation_path, corners_layer_path):
    RADIUS_SHORE_IMPACT = MAX_DIST_NODES/2
    
    shore_layer = QgsVectorLayer(shore_layer_path, '', "ogr")
    water_vegetation_layer = QgsVectorLayer(water_vegetation_path, '', "ogr")
    corners_layer = QgsVectorLayer(corners_layer_path, '', "ogr")

    nodes_layer.startEditing()
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

    index = QgsSpatialIndex(water_vegetation_layer.getFeatures())

    nodes_layer.startEditing()
    for feature in nodes_layer.getFeatures():
        #check if it is a dead end
        position = (feature.geometry().asPoint().x(), feature.geometry().asPoint().y())
        if sum(1 for _ in G.successors(position)) == 1:
            for x in G.predecessors(position):
                forward_prob = G[x][position]['transition_probability']
            # for x in G.successors(position):
                # G[position][x]['transition_probability'] = 1-forward_prob*0.5
            dead_ends_prob = 0.5*forward_prob
        else:
            dead_ends_prob = 0
        
        
        #check close sharp corners
        geom_buffer = feature.geometry().buffer(RADIUS_SHORE_IMPACT, 10)
        close_sharp_corners = np.array([feat['wind_prob'] for feat in corners_layer.getFeatures() if (feat.geometry().intersects(geom_buffer) and feat['sharp']==1)])
        sharp_corners_prob = 1-np.prod(1-0.5*close_sharp_corners)
        
        #check if shore types close to node are reasons to get stuck (houseboats or vegetation)
        close_shore_features = [feat for feat in shore_layer.getFeatures() if feat.geometry().intersects(geom_buffer)]
        for feat in close_shore_features:
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

def sensitive_area(nodes_layer, impact_factor_layer_path, G):
    impact_factor_layer = QgsVectorLayer(impact_factor_layer_path, '', "ogr")
    
    name_list = [field.name() for field in nodes_layer.fields()]
    if not 'impact_factor' in name_list: 
        nodes_layer.startEditing()
        layer_provider = nodes_layer.dataProvider()
        layer_provider.addAttributes([QgsField("impact_factor", QVariant.Double), QgsField("node_index", QVariant.Int)])
        nodes_layer.commitChanges()
        print("Added attribute field for impact factor and node index.")
    
    name_list = [field.name() for field in nodes_layer.fields()]
    impact_factor_id = name_list.index("impact_factor")
    node_index_id = name_list.index("node_index")
    
    nodes_layer.startEditing()

    for feature in nodes_layer.getFeatures():
        impact_factor = 0
        position = (feature.geometry().asPoint().x(), feature.geometry().asPoint().y())
        node_index = G.nodes[position]['label']
        nodes_layer.changeAttributeValue(feature.id(), node_index_id, int(node_index))
        for feat in impact_factor_layer.getFeatures():
            if feat.geometry().contains(feature.geometry().asPoint()):
                impact_factor = feat['impact_factor']
        nodes_layer.changeAttributeValue(feature.id(), impact_factor_id, float(impact_factor))

    nodes_layer.commitChanges()
    nodes_layer.endEditCommand()

MAX_DIST_NODES = 100

final_network_layer_path = layers_folder +"delft_final_network_exploded_d"+str(MAX_DIST_NODES)+".geojson"
final_network_layer = iface.addVectorLayer(final_network_layer_path, "final_network", "ogr")

nodes_attributes_layer_path = layers_folder + "final_network_nodes_attributes_d"+str(MAX_DIST_NODES)+"node_indices.geojson"
nodes_attributes_layer = create_nodes_layer(final_network_layer_path, nodes_attributes_layer_path)

RADIUS_SOURCES_IMPACT = 100
sources_layer_path = layers_folder + "producers_no_market_reprojected.geojson"
initial_probabilities(nodes_attributes_layer, sources_layer_path, RADIUS_SOURCES_IMPACT)

G = create_network(final_network_layer_path)
G = get_transition_probabilities(G)

polygon_layer_path = layers_folder + "waterpolygon_delft_reprojected_exploded.geojson"
polygon_layer = QgsVectorLayer(polygon_layer_path, '', "ogr")

max_boat_width_path = layers_folder + "max_boat_width_delft.geojson"
max_boat_width_layer = QgsVectorLayer(max_boat_width_path, '', "ogr")
MAX_CANAL_WIDTH = 100

catching_probabilities(nodes_attributes_layer, polygon_layer, max_boat_width_layer, MAX_CANAL_WIDTH)

shore_layer_path = layers_folder + "shore_types_delft_reprojected.geojson"
water_vegetation_path = layers_folder + "water_vegetation_delft.geojson"
corners_layer_path = layers_folder + "sharp_corners_delft.geojson"

stuck_probabilities(nodes_attributes_layer, G, shore_layer_path, MAX_DIST_NODES, water_vegetation_path, corners_layer_path)
display_probabilities_map(G, final_network_layer)

impact_factor_layer_path = layers_folder + "impact_factor_citycenter.geojson"
sensitive_area(nodes_attributes_layer, impact_factor_layer_path, G)