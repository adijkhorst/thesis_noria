folder = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts/"
file = 'init_prob_uniform_308nodes.txt'
file = '198nodes.txt'
# file = '244nodes.txt'
# file = '308nodes.txt'

# file = '444nodes_B2.txt'
# file = '522nodes_B2.txt'
# file = '622nodes_B2.txt'
# file = '784nodes_B2.txt'

# file = '622nodes_B2.txt'
# file = '622nodes_fixed_solutions_B2.txt'
file = 'heuristic_198nodes.txt'
# file = 'heuristic_622nodes_B2.txt'

# file = '522nodes_B2.txt'
# file = '622nodes_fixed_solutions_d60.txt'

file = 'water_veg_0percent_308nodes_B2.txt'
# file = 'heuristic_water_veg_0percent_308nodes_B2.txt'
file = 'output_groningen/583nodes.txt'
file = 'output_groningen/1161nodes_fixed_solutions_d100.txt'
file = 'output_groningen/1161nodes_B16.txt'
solution_file_path = folder + file
B = 1

### read solution file
with open(solution_file_path) as f:
    run1 = f.readlines()
run1 = [eval(line.strip()) for line in run1]

temp_layer = QgsVectorLayer("Point?crs=EPSG:28992","solution_layer_"+file,"memory")

temp_layer.startEditing()
if file[-25:] == 'nodes_fixed_solutions.txt' or file[-29:] == 'nodes_fixed_solutions_d60.txt' or file[-30:] == 'nodes_fixed_solutions_d100.txt' or file[-13:] == 'solutions.txt':
    index = round(B/0.2-1)
    for catching_system in run1[index]:
                point = QgsPointXY(catching_system[0], catching_system[1])
                new_feature = QgsFeature()
                new_feature.setGeometry(QgsGeometry.fromPointXY(point))
                new_feature.setAttributes([])#[:len(test_layer.attributeList())])
                temp_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)

else: 
    for index, line in enumerate(run1[1:]):
        if round(float(line[0]), 1) == B:
            for catching_system in run1[index+1][-1]:
                # locations = [list(i[-1]) for i in run1[index][-1]]
                # types = [i[1] for i in run1[index][-1]]
                point = QgsPointXY(catching_system[2][0], catching_system[2][1])
                new_feature = QgsFeature()
                new_feature.setGeometry(QgsGeometry.fromPointXY(point))
                new_feature.setAttributes([])#[:len(test_layer.attributeList())])
                temp_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
            
temp_layer.updateExtents()
temp_layer.commitChanges()
temp_layer.endEditCommand()

QgsProject.instance().addMapLayer(temp_layer)



### TEST STYLE STUFF

# symbol = QgsMarkerSymbol.createSimple({'name': 'square', 'color': 'red'})
# layer.renderer().setSymbol(symbol)
# # show the change
# layer.triggerRepaint()


# vlayer.renderer().symbol().setColor(QColor("blue"))
# vlayer.triggerRepaint()



##### PLOT PLASTIC WASTE FLOW
# import networkx as nx

# MAX_DIST_NODES = 150
# layers_folder = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/"
# nodes_layer_path = layers_folder + "final_network_nodes_attributes_d"+str(MAX_DIST_NODES)+".geojson"

# nodes_layer = QgsVectorLayer(nodes_layer_path, 'nodes_attributes_d'+str(MAX_DIST_NODES), "ogr")
# QgsProject.instance().addMapLayer(nodes_layer)
# name_list = [field.name() for field in nodes_layer.fields()]
# if (not 'catching_system_type' in name_list) and (not 'plastic_flow' in name_list):

#     nodes_layer.startEditing()
#     layer_provider = nodes_layer.dataProvider()
#     layer_provider.addAttributes([QgsField('catching_system_type', QVariant.Int), QgsField('plastic_flow', QVariant.Double)])
#     nodes_layer.commitChanges()

# name_list = [field.name() for field in nodes_layer.fields()]
# # catching_type_id = name_list.index("catching_system_type")
# plastic_flow_id = name_list.index("plastic_flow")

# G = nx.read_gml(folder + "/pulp_scripts/d"+str(MAX_DIST_NODES)+".gml")
# # solution_nodes = nx.get_node_attributes(G, 'catching_system_type')

# nodes_layer.startEditing()
# for feature in nodes_layer.getFeatures():
#     coords = '('+str(feature.geometry().asPoint().x())+','+str(feature.geometry().asPoint().y())+')'
#     nodes_layer.changeAttributeValue(feature.id(), plastic_flow_id, float(G.nodes[coords]['plastic_flow']))
#     # if coords in solution_nodes.keys():
#     #     type = solution_nodes[coords]
#     #     print(nodes_layer.changeAttributeValue(feature.id(), catching_type_id, type))
        

# # Refresh map
# nodes_layer.commitChanges()
# nodes_layer.endEditCommand()
# iface.mapCanvas().refresh()


