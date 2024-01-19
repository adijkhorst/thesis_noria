import numpy as np

polygon_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterpolygon_delft_reprojected_exploded.geojson"
corners_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/sharp_corners_delft.geojson"

# Load layers
polygon_layer = QgsVectorLayer(polygon_layer_path, '', "ogr")
corners_layer = QgsVectorLayer("Point?crs=EPSG:28992", "sharp_corners", "memory")
layer_provider = corners_layer.dataProvider()
corners_layer.startEditing()
layer_provider.addAttributes([QgsField("bisector_angle", QVariant.Double), QgsField("azimuth_previous", QVariant.Double), QgsField("angle", QVariant.Double), QgsField("sharp", QVariant.Int)])
corners_layer.commitChanges()

QgsProject.instance().addMapLayer(corners_layer)

corners_layer.startEditing()
for feature in polygon_layer.getFeatures():
    # print(feature.geometry().asPolygon()[0])
    # break
    for polygon in feature.geometry().asPolygon():
        for index, vertex in enumerate(polygon):
            new_feature = QgsFeature()
            new_feature.setGeometry(QgsGeometry.fromPointXY(vertex))
            # new_feature.setAttributes([0, 0, 0])
            bisector = feature.geometry().angleAtVertex(index)/np.pi*180 + 90
            azimuth_previous = (polygon[index-1].azimuth(vertex) - 180) % 360
            if bisector > azimuth_previous:
                if bisector - azimuth_previous > 180:
                    angle = 2* (360 - bisector + azimuth_previous)
                else:
                    angle = 2*(bisector - azimuth_previous)
            else:
                angle = 2* (azimuth_previous - bisector)
            sharp = 0
            if angle < 110:
                sharp = 1
            
            #filter out points that are on the edge of two polygons
            point_buffer = new_feature.geometry().buffer(1, -1)
            close_polygons = [feat for feat in polygon_layer.getFeatures() if feat.geometry().intersects(point_buffer)]
            if len(close_polygons) > 1:
                sharp = 0
            
            new_feature.setAttributes([bisector, azimuth_previous, angle, sharp])#[:len(test_layer.attributeList())])
            corners_layer.addFeature(new_feature, QgsFeatureSink.FastInsert)
        # print(vertex)
        # print('angle: ', feature.geometry().angleAtVertex(index))


corners_layer.updateExtents()
corners_layer.commitChanges()
corners_layer.endEditCommand()

iface.mapCanvas().refresh()

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
