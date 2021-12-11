# Code by Armin Nakhjiri
# Contact me at Nakhjiri.Armin@gmail.com

import os
from PIL import Image, ExifTags
import arcpy
# Import packages

imageFolder = arcpy.GetParameterAsText(0)
# The contents of the folder has to be images ONLY!
fileName = arcpy.GetParameterAsText(1)
outpath = arcpy.GetParameterAsText(2)
# set an outpath for the shapefile


folderContent = os.listdir(imageFolder)
# Put folder contents in a list
shapefile = r'{}\{}.shp'.format(outpath, fileName)
# build a shapefile based on user input

shapeList = []
spatialReference = arcpy.SpatialReference(4326)
# specify coordinate system


def shape_developer():
    # define a function to extract data and build a shapefile
    pt = arcpy.Point()
    ptGeoms = []

    for p in shapeList:
        pt.X = p[0]
        pt.Y = p[1]
        ptGeoms.append(arcpy.PointGeometry(pt, spatialReference))
        # get x and y from shp_list and append in ptGeoms list as geometry of points (location)

    arcpy.CopyFeatures_management(ptGeoms, shapefile)
    arcpy.AddXY_management(shapefile)
    arcpy.AddField_management(shapefile, "timestamp", "TEXT", 9, "", "", "refcode", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(shapefile, "img_path", "TEXT", 9, "", "", "refcode", "NULLABLE", "REQUIRED")
    # Add fields to the attribute table

    count = 0

    with arcpy.da.UpdateCursor(shapefile, ["timestamp", "img_path"]) as cursor:

        for c in cursor:
            c[0] = shapeList[count][3]
            # set timestamp
            c[1] = shapeList[count][2]
            # set image path on os
            count += 1
            cursor.updateRow(c)
            # Add rows


def coordinates_converter(value):
    # Define a function to convert coordinates to decimal degrees
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


arcpy.AddMessage('Checking Image info...')

for image in folderContent:
    # Extracting values from metadata
    fullImagePath = os.path.join(imageFolder, image)

    pil_img = Image.open(fullImagePath)

    exifData = {ExifTags.TAGS[k]: v for k, v in pil_img._getexif().items() if k in ExifTags.TAGS}

    allGPS = {}

    try:
        imageTime = (exifData['DateTime'])

        for key in exifData['GPSInfo'].keys():
            decoded_value = ExifTags.GPSTAGS.get(key)
            allGPS[decoded_value] = exifData['GPSInfo'][key]

        lon_ref = allGPS.get('GPSLongitudeRef')
        lat_ref = allGPS.get('GPSLatitudeRef')

        lon = allGPS.get('GPSLongitude')
        lat = allGPS.get('GPSLatitude')

        if lon_ref == "W":
            decimalLon = -abs(coordinates_converter(lon))
        else:
            decimalLon = coordinates_converter(lon)
        if lat_ref == "S":

            decimalLat = -abs(coordinates_converter(lat))
        else:
            decimalLat = coordinates_converter(lat)

        shapeList.append([decimalLon, decimalLat, fullImagePath, imageTime])

    except:
        arcpy.AddMessage("This image had no GPS info")
        arcpy.AddMessage(fullImagePath)
        pass

arcpy.AddMessage(shapeList)
# Print Shape list
shape_developer()
# Call the shape_creator function
arcpy.AddMessage('Shapefile successfully made!')

arcpy.AddMessage('Adding to layers...')
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
newlayer = arcpy.mapping.Layer(shapefile)
arcpy.mapping.AddLayer(df, newlayer, "TOP")
# Add shapefile to Layer management

arcpy.AddMessage('Done.')
arcpy.AddMessage('Code by Armin Nakhjiri')


