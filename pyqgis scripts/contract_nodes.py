# 'waterway_canal_delft.geojson'
# Import necessary QGIS modules
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsWkbTypes, QgsField, QgsPoint

# Define the input line layer path and distance threshold
input_layer_path = 'waterway_canal_delft_reprojected.geojson'
distance_threshold = 100  # Adjust this value as needed (in meters)

# Load the input layer
layer = QgsVectorLayer(input_layer_path, 'input_layer', 'ogr')

# Create an empty memory layer to store the contracted graph
contracted_layer = QgsVectorLayer('LineString', 'contracted_graph', 'memory')

# Create a data provider for the memory layer
contracted_layer.dataProvider().addAttributes([QgsField('Contracted',  QVariant.Int)])

# Start an editing session for the memory layer
contracted_layer.startEditing()

# Add the memory layer to the current project
QgsProject.instance().addMapLayer(contracted_layer)

# Create a feature dictionary to store the contracted nodes and their original nodes
contracted_nodes = {}

# A flag to keep track of whether nodes have been contracted
nodes_contracted = True

# Continue contracting nodes until no more nodes can be contracted
while nodes_contracted:
    nodes_contracted = False

    # Loop through the features in the input layer
    for feature in layer.getFeatures():
        geometry = feature.geometry()
        new_geometry = QgsGeometry()

        # Check if the feature is a node (end point of a line)
        if geometry.wkbType() == QgsWkbTypes.Point:
            node_coords = geometry.asPoint()

            # Check if this node is not already contracted
            if feature.id() not in contracted_nodes:
                new_geometry = geometry
                contracted_nodes[feature.id()] = [feature.id()]

                # Loop through the other features to find nearby nodes
                for other_feature in layer.getFeatures():
                    if other_feature.id() == feature.id():
                        continue

                    other_geometry = other_feature.geometry()
                    if other_geometry.wkbType() == QgsWkbTypes.Point:
                        other_coords = other_geometry.asPoint()

                        # Calculate the distance between nodes
                        distance = node_coords.distance(other_coords)

                        # If the distance is within the threshold, contract the nodes
                        if distance <= distance_threshold:
                            new_geometry = QgsGeometry.fromPointXY(node_coords)
                            contracted_nodes[feature.id()].append(other_feature.id())

                            # Mark that nodes have been contracted
                            nodes_contracted = True

        # Add the contracted node to the memory layer
        if not new_geometry.isNull():
            contracted_feature = QgsFeature(contracted_layer.fields())
            contracted_feature.setGeometry(new_geometry)
            contracted_feature['Contracted'] = 1
            contracted_layer.dataProvider().addFeatures([contracted_feature])

# Commit changes to the memory layer
contracted_layer.commitChanges()

# Refresh the map canvas to see the contracted layer in QGIS
iface.mapCanvas().refreshAllLayers()

# Print a summary of contracted nodes
print("Contracted Nodes:")
for node, neighbors in contracted_nodes.items():
    print(f"Node {node} contracted with nodes {neighbors}")

print("Contracting nodes completed.")
