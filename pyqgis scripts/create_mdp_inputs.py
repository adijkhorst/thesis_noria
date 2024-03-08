### input: final layer of directed network
### output: vector initial distribution, transition matrix including probability of getting stuck, proportion of waterway that can be blocked (betas)

# also display transition probabilities, getting stuck, init distr, betas
import numpy as np

RADIUS_SOURCES_IMPACT = 100

def create_nodes_layer(final_network_layer_path, nodes_attributes_layer_path):
    nodes_attributes_layer = processing.run("native:extractvertices", {'INPUT': final_network_layer_path,
               'OUTPUT': 'TEMPORARY_OUTPUT'})["OUTPUT"]
    nodes_attributes_layer = processing.run("native:deleteduplicategeometries", {'INPUT': nodes_attributes_layer,
                'OUTPUT': nodes_attributes_layer_path})
    
    nodes_attributes_layer = iface.addVectorLayer(nodes_attributes_layer_path, "nodes_attributes", "ogr")
    
    ### add fields for initial probabilities, stuck probabilities and catching probabilities
    nodes_attributes_layer.startEditing()
    layer_provider = nodes_attributes_layer.dataProvider()
    layer_provider.addAttributes([QgsField('init_probability', QVariant.Double), QgsField('stuck_probability', QVariant.Double), QgsField('catching_probability', QVariant.Double)])
    nodes_attributes_layer.commitChanges()
    
    init_prob_id, stuck_prob_id, catch_prob_id = nodes_attributes_layer.attributeList()[-3], nodes_attributes_layer.attributeList()[-2], nodes_attributes_layer.attributeList()[-1]
    
    
    
    
def initial_probabilities(nodes_layer, sources_layer_path, radius_impact):
    sources_layer = QgsVectorLayer(sources_layer_path, '', "ogr") #will not be edited
    

def transition_matrix():
    pass
    
    
if __name__ == '__main__':
    sources_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/producers_no_market_reprojected.geojson"
    
    final_network_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_directed_exploded.geojson"
    nodes_attributes_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/nodes_attributes.geojson"