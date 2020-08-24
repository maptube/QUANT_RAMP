"""
analytics.py
Produce analytic data for debugging and visualisation
"""

import pandas as pd
import os
from geojson import dump, FeatureCollection, Feature, GeometryCollection, LineString, MultiLineString

from globals import *
from utils import loadMatrix
from zonecodes import ZoneCodes


"""
runAnalytics
Function to run the full analytics package
"""
def runAnalytics():
    #produce a flow geojson for the top flows from a probability matrix e.g. retail flows, school flows or hospital flows
    runAnalyticsRetail(0.004) #was 0.002 then 0.008
    #runAnalyticsSchools(0.008)
    #runAnalyticsHospitals(0.008)
    

################################################################################

"""
graphProbabilities
Produce graph data for the retail, schools and hospitals model
@param threshold The threshold below which to ignore low probability trips
@param dfPointsPopulation MSOA list
@param dfPointsZones Point list
@param pointsProbSij matrix of probabilities
@param pointsZonesIDField field name of the unique identifier field in the points files e.g. school id, retail id etc
@returns a feature collection as a geojson object to be written to file (probably)
"""
def graphProbabilities(threshold,dfPointsPopulation,dfPointsZones,pointsProbSij,pointsZonesIDField):

    #east,north in retail points zones file (look in zonecodes for the lat lon)
    #east, north and lat,lon in retail points population file

    count=0
    features = []
    m,n = pointsProbSij.shape
    for i in range(m): #this is the zonei
        row_i = dfPointsPopulation.loc[dfPointsPopulation['zonei'] == i]
        i_msoaiz = row_i['msoaiz'].values[0]
        i_east = float(row_i['osgb36_east'].values[0])
        i_north = float(row_i['osgb36_north'].values[0])
        print("graphProbabilities ",i_msoaiz,count)
        for j in range(n):
            p = pointsProbSij[i,j]
            if p>=threshold:
                row2 = dfPointsZones.loc[dfPointsZones['zonei'] == j] #yes, zonei==j is correct, they're always called 'zonei'
                j_id = str(row2[pointsZonesIDField].values[0]) #won't serialise a float64 otherwise!
                j_east = float(row2['east'].values[0])
                j_north = float(row2['north'].values[0])
                the_geom = LineString([(i_east,i_north),(j_east,j_north)])
                f = Feature(geometry=the_geom, properties={"o": i_msoaiz, "d": j_id, "prob":p})
                features.append(f)
                count+=1
            #end if
        #end for
    #end for
    return FeatureCollection(features)

################################################################################

"""
runAnalyticsRetail
@param threshold any probability of trip between MSOA and point below this threshold is cut
"""
def runAnalyticsRetail(threshold):
    dfRetailPointsPopulation = pd.read_csv(data_retailpoints_population)
    dfRetailPointsZones = pd.read_csv(data_retailpoints_zones)
    retailpoints_probSij = loadMatrix(data_retailpoints_probSij)

    fc = graphProbabilities(threshold,dfRetailPointsPopulation,dfRetailPointsZones,retailpoints_probSij,'id')

    #and save fc as a geojson
    with open(os.path.join(modelRunsDir,'analytic_retail.geojson'), 'w') as f:
        dump(fc, f)

################################################################################

"""
runAnalyticsSchools
NOTE: runs primary AND secondary schools
@param threshold any probability of trip between MSOA and point below this threshold is cut
"""
def runAnalyticsSchools(threshold):
    #primary schools
    dfPrimaryPopulation = pd.read_csv(data_primary_population)
    dfPrimaryZones = pd.read_csv(data_primary_zones)
    primary_probPij = loadMatrix(data_primary_probPij)

    fc = graphProbabilities(threshold,dfPrimaryPopulation,dfPrimaryZones,primary_probPij,'URN')

    #and save fc as a geojson
    with open(os.path.join(modelRunsDir,'analytic_primary.geojson'), 'w') as f:
        dump(fc, f)

    #secondary schools
    dfSecondaryPopulation = pd.read_csv(data_secondary_population)
    dfSecondaryZones = pd.read_csv(data_secondary_zones)
    secondary_probPij = loadMatrix(data_secondary_probPij)

    fc = graphProbabilities(threshold,dfSecondaryPopulation,dfSecondaryZones,secondary_probPij,'URN')

    #and save fc as a geojson
    with open(os.path.join(modelRunsDir,'analytic_secondary.geojson'), 'w') as f:
        dump(fc, f)

################################################################################

def runAnalyticsHospitals(threshold):
    dfHospitalPopulation = pd.read_csv(data_hospital_population)
    dfHospitalZones = pd.read_csv(data_hospital_zones)
    hospital_probHij = loadMatrix(data_hospital_probHij)

    fc = graphProbabilities(threshold,dfHospitalPopulation,dfHospitalZones,hospital_probHij,'name') #or there's an id too

    #and save fc as a geojson
    with open(os.path.join(modelRunsDir,'analytic_hospital.geojson'), 'w') as f:
        dump(fc, f)

################################################################################
