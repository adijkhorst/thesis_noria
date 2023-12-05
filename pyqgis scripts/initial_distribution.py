import numpy as np

RADIUS_SOURCES_IMPACT = 100

nodes_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/delft_allnodes.geojson"
sources_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/producers_no_market_reprojected.geojson"

# Add the sources layer as a variable (will not be edited)
sources_layer = QgsVectorLayer(sources_layer_path, '', "ogr")

# Create a new layer for modifications (load the new layer again from the new GeoJSON file)
new_layer = iface.addVectorLayer(nodes_layer_path, "NewLayer", "ogr")

# Check if the layer is valid
if not new_layer.isValid() or not sources_layer.isValid():
    print("Layer failed to load!")

new_layer.startEditing()
layer_provider = new_layer.dataProvider()
layer_provider.addAttributes([QgsField('init_probability', QVariant.Double)])
new_layer.commitChanges()
attr_id = new_layer.attributeList()[-1]

### Create numpy array with columns: x_coordinate, y_coordinate, probability
n_features = new_layer.featureCount()
n_sources = sources_layer.featureCount()

attribute_table = np.zeros((n_features, 3))

for index, feature in enumerate(new_layer.getFeatures()):
    attribute_table[index, 0] = feature.geometry().asPoint().x()
    attribute_table[index, 1] = feature.geometry().asPoint().y()

sources_locations = np.zeros((n_sources, 2))
for index, feature in enumerate(sources_layer.getFeatures()):
    sources_locations[index, 0] = feature.geometry().asPoint().x()
    sources_locations[index, 1] = feature.geometry().asPoint().y()

for i in range(n_features):
    dists = np.sqrt(np.sum(np.square(sources_locations - np.repeat([attribute_table[i][:2]], n_sources, axis = 0)), axis = 1))
    attribute_table[i, 2] = len(np.where(dists < RADIUS_SOURCES_IMPACT)[0])

total = np.sum(attribute_table[:,2])

new_layer.startEditing()
for index, feature in enumerate(new_layer.getFeatures()):
    f_id = feature.id()
    prob = attribute_table[index, 2]/total
    attribute_table[index, 2] = prob
    new_layer.changeAttributeValue(f_id, attr_id, float(prob))

# print(attribute_table)

new_layer.commitChanges()
new_layer.endEditCommand()
iface.mapCanvas().refresh()

# options = QgsVectorFileWriter.SaveVectorOptions()
# options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
# options.layerOptions = ["PRECISION=NO"]
# QgsVectorFileWriter.writeAsVectorFormatV2(line_layer, new_layer_path, QgsCoordinateTransformContext(), options)
