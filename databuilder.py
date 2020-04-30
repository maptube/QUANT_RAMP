"""
QUANT_RAMP
databuilder.py

Build data for project
TODO: this is supposed to collect and build all external data - using hand crafted data for initial tests
At the moment, it builds model-runs/retailpoints_geocoded.csv with oa geocoded Geolytix retail points
"""
import os
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from shapely.strtree import STRtree
import csv

from globals import *

"""
geocodeGeolytix
Geocode the geolytix point file by appending an OA code and an MSOA code.
Write out csv file containing the geocoded geolytix data.
The file name consts below are defined in globals.py
PRE:
  requires "data_oa_shapefile" which points to the infuse OA boundary file for E, W, S and NI
  requires "data_msoa_shapefile" similarly for the MSOA boundary file
  requires "data_geolytix_retailpoints" containing the Geolytix Retail Points csv file
POST:
  generates "data_retailpoints_geocoded" containing the Geolytix retail point data geocoded with OA and MSOA
"""
def geocodeGeolytix():
    #read OA shapefile
    print("loading oa shapefile from: ",data_oa_shapefile)
    oa_boundary = gpd.read_file(data_oa_shapefile)
    print(data_oa_shapefile,len(oa_boundary),"rows")
    #print(oa_boundary.head(6))
    #print(oa_boundary.shape)
    # plot the data using geopandas .plot() method - TAKES AGES THOUGH!
    #fig, ax = plt.subplots(figsize = (10,10))
    #oa_boundary.plot(ax=ax)
    #plt.show()

    #read MSOA shapefile
    print("loading msoa shapefile from: ",data_msoa_shapefile)
    msoa_boundary = gpd.read_file(data_msoa_shapefile)
    print(data_msoa_shapefile,len(msoa_boundary),"rows")

    #read geolytix retail data
    #id,retailer,fascia,store_name,add_one,add_two,town,suburb,postcode,long_wgs,lat_wgs,bng_e,bng_n,pqi,open_date,size_band
    #1010004593,Tesco,Tesco Express,Tesco Eastern Seaside Road Express,133-135 Seaside Road,,Eastbourne,Meads,BN21 3PA,0.293276318,50.76901815,561808.4009,99110.41946,Rooftop geocoded by Geolytix,,"< 3,013 ft2 (280m2)"
    #size bands: "< 3,013 ft2 (280m2)" "15,069 < 30,138 ft2 (1,400 < 2,800 m2)" "3,013 < 15,069 ft2 (280 < 1,400 m2)" "30,138 ft2 > (2,800 m2)"
    medianSizeBands = {
        "< 3,013 ft2 (280m2)": 140.0,
        "3,013 < 15,069 ft2 (280 < 1,400 m2)": 840.0,
        "15,069 < 30,138 ft2 (1,400 < 2,800 m2)": 2100.0,
        "30,138 ft2 > (2,800 m2)": 2800.0
    }
    retailPoints = []
    print("loading retail points from: ",data_geolytix_retailpoints)
    with open(data_geolytix_retailpoints, newline = '') as csvFile:
        reader = csv.reader(csvFile,delimiter=',',quotechar='"')
        next(reader) #skip header row
        for row in reader:
            #print(row)
            fascia = row[2] #e.g. Tesco Express
            east = float(row[11])
            north = float(row[12])
            strFloorspace = row[15] #text version
            floorspace = medianSizeBands[strFloorspace]
            point = Point(east,north)
            retailPoints.append({'name':fascia,'point':point,'floorspace':floorspace})
        #end for
    #end with
    print(data_geolytix_retailpoints,len(retailPoints),"rows")

    #that's the data loaded, now need to do something with it...

    #point in polygon on the oa boundaries using geopandas in-built spatial index to find out which oa and msoa each
    #retail point is in
    oa_retail_count = {} #keyed on oa, contains count of how many retail points in each oa
    retail_oa_zone_code = {} #keyed on retailPoints index id, stores the od code this point is in i.e. it's a join to the retailPoints data frame
    sindex_oa = oa_boundary.sindex
    ##
    msoa_retail_count = {}
    retail_msoa_zone_code = {}
    sindex_msoa = msoa_boundary.sindex
    ##
    for retail_idx, retailer in enumerate(retailPoints):
        rp = retailer['point']
        #oa point in polygon
        possible_matches_index_oa = list(sindex_oa.intersection(rp.bounds)) #coarse match using the OA spatial index
        possible_matches_oa = oa_boundary.iloc[possible_matches_index_oa] #get actual geom back from indexes just returned
        precise_matches_oa = possible_matches_oa[possible_matches_oa.intersects(rp)] #perform expensive precise match using geom
        #msoa point in polygon
        possible_matches_index_msoa = list(sindex_msoa.intersection(rp.bounds)) #coarse match using the MSOA spatial index
        possible_matches_msoa = msoa_boundary.iloc[possible_matches_index_msoa] #get actual geom back from indexes just returned
        precise_matches_msoa = possible_matches_msoa[possible_matches_msoa.intersects(rp)] #perform expensive precise match using geom
        #print(precise_matches) #it's a geodataframe object
        count_oa = len(precise_matches_oa)
        count_msoa = len(precise_matches_msoa)
        #assert... should never happen
        if count_oa>1 or count_msoa>1:
            print("error: retail point in more than one output area or msoa: ",retailer,precise_matches_oa, precise_matches_msoa)
        #end assert
        #assert... of course you could also check that precise_matches isn't empty as we have points for channel isles and isle of man, but no OAs
        if count_oa==0 or count_msoa==0:
            print("count=0 for ",rp)
            continue
        #end second assert
        match_oa = precise_matches_oa.iloc[0] #ugly
        match_msoa = precise_matches_msoa.iloc[0] #ugly
        oa_code = match_oa.geo_code
        msoa_code = match_msoa.geo_code
        if oa_code in oa_retail_count:
            oa_retail_count[oa_code]+=1 #increment exising key
        else:
            oa_retail_count[oa_code]=1 #new key
        retail_oa_zone_code[retail_idx]=oa_code #store the oa that this retail point sits inside by index
        #and now for the msoa
        if msoa_code in msoa_retail_count:
            msoa_retail_count[msoa_code]+=1 #increment exising key
        else:
            msoa_retail_count[msoa_code]=1 #new key
        retail_msoa_zone_code[retail_idx]=msoa_code #store the oa that this retail point sits inside by index
    #end for
    print('oa_retail_count contains: ',len(oa_retail_count),'separate output areas containing retail points')
    print('msoa_retail_count contains: ',len(msoa_retail_count),'separate mid layer super output areas containing retail points')
    print('total retail points: ',len(retailPoints))

    #now write out a retail points file with oa attached to the retail points
    with open(data_retailpoints_geocoded, 'w', newline = '') as csvFile:
        writer = csv.writer(csvFile,delimiter=',')
        writer.writerow(['name','east','north','floorspace','oa','msoa'])
        for idx, rp in enumerate(retailPoints):
            if idx in retail_oa_zone_code:
                writer.writerow([ rp['name'], rp['point'].x, rp['point'].y, rp['floorspace'], retail_oa_zone_code[idx], retail_msoa_zone_code[idx] ])
        #end for
    #end with

    #could also write out the opposite data - oa to point lookup, although that's one to many
#end def geocodeGeolytix

################################################################################

