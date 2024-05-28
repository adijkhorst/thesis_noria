import os
folder = os.getcwd()
folder = QgsProject.instance().readPath("./")
sys.path.insert(1, folder + "\\pyqgis_scripts")
import find_dmax

MAX_DIST_NODES = find_dmax.find_dmax()
solution_file_path = folder + '\\pulp_scripts\\solution.txt'

### read solution file
with open(solution_file_path) as f:
    run1 = f.readlines()
run1 = [eval(line.strip()) for line in run1]

temp_layer = QgsVectorLayer("Point?crs=EPSG:28992","solution_layer","memory")
attributes_layer = QgsVectorLayer(folder+'\\final_network_nodes_attributes_d'+str(int(MAX_DIST_NODES))+'.geojson', '', 'ogr')

temp_layer.startEditing()
layer_provider = temp_layer.dataProvider()
layer_provider.addAttributes([QgsField('type', QVariant.Int), QgsField('angle', QVariant.Double), QgsField('catching_probability', QVariant.Double), QgsField('plastic_flow', QVariant.Double), QgsField('flow_caught', QVariant.Double)])
temp_layer.commitChanges()


temp_layer.startEditing()
for index, line in enumerate(run1[1:]):
    for catching_system in run1[index+1][-1]:
        # locations = [list(i[-1]) for i in run1[index][-1]]
        # types = [i[1] for i in run1[index][-1]]
        point = QgsPointXY(catching_system[2][0], catching_system[2][1])
        for feature in attributes_layer.getFeatures():
            if feature.geometry().asPoint() == point:
                angle = feature['angle']
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPointXY(point))
        type = catching_system[1]
        new_feature.setAttributes([type, angle, catching_system[3], catching_system[4], round(catching_system[5], 3)])#[:len(test_layer.attributeList())])
        temp_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
temp_layer.updateExtents()
temp_layer.commitChanges()
temp_layer.endEditCommand()

QgsProject.instance().addMapLayer(temp_layer)

##### PLOT PLASTIC WASTE FLOW IN OLD NODES_ATTRIBUTES LAYER
import networkx as nx

nodes_layer_path = folder + "\\final_network_nodes_attributes_d"+str(MAX_DIST_NODES)+".geojson"

nodes_layer = QgsVectorLayer(nodes_layer_path, 'nodes_attributes_d'+str(MAX_DIST_NODES), "ogr")
QgsProject.instance().addMapLayer(nodes_layer)
name_list = [field.name() for field in nodes_layer.fields()]
if not 'plastic_flow' in name_list:
    nodes_layer.startEditing()
    layer_provider = nodes_layer.dataProvider()
    layer_provider.addAttributes([QgsField('plastic_flow', QVariant.Double)])
    nodes_layer.commitChanges()

name_list = [field.name() for field in nodes_layer.fields()]
plastic_flow_id = name_list.index("plastic_flow")

G = nx.read_gml(folder + "\\pulp_scripts\\solution.gml")

nodes_layer.startEditing()
for feature in nodes_layer.getFeatures():
    coords = '('+str(feature.geometry().asPoint().x())+','+str(feature.geometry().asPoint().y())+')'
    nodes_layer.changeAttributeValue(feature.id(), plastic_flow_id, float(G.nodes[coords]['plastic_flow']))

# # Refresh map
nodes_layer.commitChanges()
nodes_layer.endEditCommand()
iface.mapCanvas().refresh()