import numpy as np

current_directory = QgsProject.instance().readPath("./")
sys.path.insert(1, current_directory + "\\pulp_scripts")
import wind_data

polygon_layer_path = current_directory + "\\QGIS_layers\\waterpolygons.geojson"

def write_sharp_corners_file(polygon_layer_path):
    # Load layers
    polygon_layer = QgsVectorLayer(polygon_layer_path, '', "ogr")
    corners_layer = QgsVectorLayer("Point?crs=EPSG:28992", "sharp_corners", "memory")
    layer_provider = corners_layer.dataProvider()
    corners_layer.startEditing()
    layer_provider.addAttributes([QgsField("bisector_angle", QVariant.Double), QgsField("azimuth_previous", QVariant.Double), \
                                QgsField("angle", QVariant.Double), QgsField("sharp", QVariant.Int), QgsField("wind_range_min", \
                                QVariant.Double), QgsField("wind_range_max", QVariant.Double), QgsField("wind_prob", QVariant.Double)])
    corners_layer.commitChanges()

    QgsProject.instance().addMapLayer(corners_layer)

    wind_directions = wind_data.get_wind_directions(2022)

    corners_layer.startEditing()
    for feature in polygon_layer.getFeatures():
        for polygon in feature.geometry().asPolygon():
            for index, vertex in enumerate(polygon):
                new_feature = QgsFeature()
                new_feature.setGeometry(QgsGeometry.fromPointXY(vertex))
                bisector = (feature.geometry().angleAtVertex(index)/np.pi*180 + 90) % 360
                azimuth_previous = (polygon[index-1].azimuth(vertex) - 180) % 360
                if bisector > azimuth_previous:
                    if bisector - azimuth_previous > 180:
                        angle = 2* (360 - bisector + azimuth_previous)
                    else:
                        angle = 2*(bisector - azimuth_previous)
                else:
                    angle = 2* (azimuth_previous - bisector)
                sharp = 0
                wind_range_min = 0
                wind_range_max = 0
                if angle < 110:
                    sharp = 1
                    wind_range_min = (bisector + 180 - angle/2) % 360
                    wind_range_max = (bisector + 180 + angle/2) % 360
                
                #filter out points that are on the edge of two polygons
                point_buffer = new_feature.geometry().buffer(1, -1)
                close_polygons = [feat for feat in polygon_layer.getFeatures() if feat.geometry().intersects(point_buffer)]
                if len(close_polygons) > 1:
                    sharp = 0
                
                if sharp == 1:
                    # add probability of getting caught in each corner as attribute
                    days = len(wind_directions)*[False]
                    if wind_range_min < wind_range_max:
                        booleans = (wind_directions > wind_range_min) & (wind_directions < wind_range_max)
                    else:
                        booleans = (wind_directions > wind_range_min) | (wind_directions < wind_range_max)
                    days = np.any([days, booleans], axis = 0)
                    wind_prob = len(wind_directions[days])/len(wind_directions)
                else:
                    wind_prob = 0
                
                new_feature.setAttributes([bisector, azimuth_previous, angle, sharp, wind_range_min, wind_range_max, wind_prob])#[:len(test_layer.attributeList())])
                corners_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
            # print(vertex)
            # print('angle: ', feature.geometry().angleAtVertex(index))
        
            break #because the first polygon is the outline, the second polygon are inner cut outs of polygons which will give wrong angles


    corners_layer.updateExtents()
    corners_layer.commitChanges()
    corners_layer.endEditCommand()

    iface.mapCanvas().refresh()

write_sharp_corners_file(polygon_layer_path)

### NOG IETS SCHRIJVEN OM CORNERS LAYER OP TE SLAAN!

### used this code to turn around one polygon part that was oriented counterclockwise instead of clockwise: + hand deleted the old feature and set the id of the new feature
# polygon_layer.startEditing()
# for feature in polygon_layer.getFeatures():
#     if feature.id() == 558:
#         vertex_list = feature.geometry().asPolygon()
#         vertex_list[0].reverse()
#         new_feature = QgsFeature()
#         new_feature.setGeometry(QgsGeometry.fromPolygonXY(vertex_list))
#         new_feature.setAttributes(feature.attributes())
#         new_feature.setAttribute(0, 1)
#         polygon_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
# polygon_layer.commitChanges()
# polygon_layer.endEditCommand()
# iface.mapCanvas().refresh()
