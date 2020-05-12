"""
costs.py
Create costs matrices e.g. from an MSOA->MSOA matrix, make an MSOA to geocoded point cost matrix
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from shapely.strtree import STRtree

from globals import modelRunsDir, QUANTCijRoadCentroidsFilename

"""
costMSOAToPoint
Take the MSOA to MSOA cost matrix and build a variant for MSOA to a point dataset based on 
MSOA to MSOA plus an additional straight line distance from the point to the nearest
MSOA centroid

The Plan:
    foreach point in points
    find closest msoa
    find distance offset to closest msoa and delta time (crowfly time to this nearest msoa to point)
    foreach MSOA
    lookup MSOA to closest MSOA (from cij) plus delta time
    write MSOA->point matrix with cij + delta time to point

NOTE: also see databuilder.computeGeolytixCosts() for the same basic methodology
PRE: uses the QUANTCijRoadCentroidsFilename file from model-runs for the cij centroid points - not same as zonecodes
@param cij cost matrix for MSOA to MSOA, zones identified by zonecodes (numpy array)
@param dfPoints the DataFrame containing [zonei,east,north] for our points
@returns an matrix that is count(points) x count(zonecodes) (i.e. cols x rows so [pointi,zonecodei])
"""
def costMSOAToPoint(cij,dfPoints):

    #const to define what speed we travel the additional distance to the retail point e.g. 30mph = 13 ms-1
    metresPerSec = 13.0

    #read in the road centroids for the cij matrix
    df = pd.read_csv(os.path.join(modelRunsDir,QUANTCijRoadCentroidsFilename))
    #code this into a geodataframe so we can make a spatial index
    gdf = gpd.GeoDataFrame(df, crs='epsg:4326', geometry=gpd.points_from_xy(df.vertex_lon, df.vertex_lat))
    #but it's lat/lon and we want east/north
    centroids = gdf.to_crs("EPSG:27700") #there, that's better
    dest_unary = centroids["geometry"].unary_union # and need this join for the centroid points nearest lookup

    #create a new MSOA to points cost matix
    m, n = cij.shape
    p, cols = dfPoints.shape
    print("array size = ",p,m)
    #NO! better below cijpoint = np.arange(m*p,dtype=np.float).reshape(m, p) #so m=MSOA and p=points index
    cijpoint = np.zeros(m*p,dtype=np.float).reshape(m,p) #so m=MSOA and p=points index
    
    #now make the amended cost function
    count=0
    for row in dfPoints.itertuples(index = False): #NOTE: iterating over Pandas rows is supposed to be bad - how else to do this?
        if (count%100==0):
            print("costs::costMSOAToPoint ",count,"/",p)
        count+=1
        p_zonei = getattr(row,'zonei')
        p_east = getattr(row,'east')
        p_north = getattr(row,'north')
        near = nearest_points(Point(p_east,p_north),dest_unary)
        match_geom = centroids.loc[centroids.geometry==near[1]]
        pmsoa_zonei = int(match_geom.zonei) #closest point msoa zone
        pmsoa_pt = match_geom.geometry
        pmsoa_east=float(pmsoa_pt.centroid.x)
        pmsoa_north=float(pmsoa_pt.centroid.y)

        dx = p_east-pmsoa_east
        dy = p_north-pmsoa_north
        dist = np.sqrt(dx*dx+dy*dy) #dist between point and centroid used for shortest path
        #work out an additional delta cost based on increased time getting from this point to the centroid
        deltaCost = (dist/metresPerSec)/60.0 #transit time in mins

        #now write every cij value for msoa_zonei to p_zonei (closest) PLUS deltaCose for p_zonei to actual point
        for i in range(n):
            C1 = cij[pmsoa_zonei,i] #yes, this is right for a trip from MSOA to closest point MSOA - QUANT is BACKWARDS
            cijpoint[i,p_zonei] = C1 + deltaCost
            #NOTE: you can only go in one direction with a matrix that is asymmetric
        #end for
    #end for

    #todo: do you want to do a sanity check for any zero values in the matrix?

    return cijpoint
        
################################################################################
    