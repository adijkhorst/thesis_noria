import networkx as nx

### first create point layer with nodes that will get init_distribution attribute
line_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_directed_exploded.geojson"
nodes_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/solutions.geojson"

### if file exists!!!
# nodes_layer = processing.run("native:extractvertices", {'INPUT': line_layer_path,
#                'OUTPUT': 'TEMPORARY_OUTPUT'})["OUTPUT"]
# nodes_layer = processing.run("native:deleteduplicategeometries", {'INPUT': nodes_layer,
#                 'OUTPUT': nodes_layer_path})

name_list = [field.name() for field in nodes_layer.fields()]
if (not 'catching_system_type' in name_list) and (not 'plastic_flow' in name_list):
    nodes_layer = QgsVectorLayer(nodes_layer_path, 'solutions', "ogr")
    QgsProject.instance().addMapLayer(nodes_layer)
    nodes_layer.startEditing()
    layer_provider = nodes_layer.dataProvider()
    layer_provider.addAttributes([QgsField('catching_system_type', QVariant.Int), QgsField('plastic_flow', QVariant.Double)])
    nodes_layer.commitChanges()

name_list = [field.name() for field in nodes_layer.fields()]
catching_type_id = name_list.index("catching_system_type")
plastic_flow_id = name_list.index("plastic_flow")

G = nx.read_gml("C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts/pulp/test.gml")
solution_nodes = nx.get_node_attributes(G, 'catching_system_type')

nodes_layer.startEditing()
for feature in nodes_layer.getFeatures():
    coords = '('+str(feature.geometry().asPoint().x())+','+str(feature.geometry().asPoint().y())+')'
    nodes_layer.changeAttributeValue(feature.id(), plastic_flow_id, float(G.nodes[coords]['plastic_flow']))
    if coords in solution_nodes.keys():
        type = solution_nodes[coords]
        print(nodes_layer.changeAttributeValue(feature.id(), catching_type_id, type))
        

# Refresh map
nodes_layer.commitChanges()
nodes_layer.endEditCommand()
iface.mapCanvas().refresh()


