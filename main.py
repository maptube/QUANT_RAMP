"""
QUANT_RAMP
main.py
"""

import os
import time
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.strtree import STRtree
import csv

from globals import *
from utils import loadQUANTMatrix, loadCSV, loadMatrix, saveMatrix, zonecodeIndexData
from zonecodes import ZoneCodes
from databuilder import geocodeGeolytix, computeGeolytixCosts, buildSchoolsPopulationTableEnglandWales, buildSchoolsPopulationTableScotland
from incometable import IncomeTable
from attractions import attractions_msoa_floorspace_from_retail_points
from quantretailmodel import QUANTRetailModel
from quantschoolsmodel import QUANTSchoolsModel
from costs import costMSOAToPoint

################################################################################
# Initialisation                                                               #
################################################################################

#NOTE: this section provides the base data for the models that come later. This
#will only be run on the first run of the program to assemble all the tables
#required from the original sources. After that, if the file exists in the
#directory, then nothing new is created and this section is effectively
#skipped, up until the model run section at the end.

#databuilder.py - run the code there...
if not os.path.isfile(data_retailpoints_geocoded):
    geocodeGeolytix()

#make geolytix costs file which is a csv of origin to destination zone with a cost
#computeGeolytixCosts()

#databuilder.py - build schools population table if needed - requires QS103 AND QS103SC on DZ2001 for Scotland
if not os.path.isfile(data_schoolagepopulation_englandwales):
    buildSchoolsPopulationTableEnglandWales()

if not os.path.isfile(data_schoolagepopulation_scotland):
    buildSchoolsPopulationTableScotland()

#now join England/Wales and Scotland files together as it should have been in the first instance!
if not os.path.isfile(data_schoolagepopulation):
    df1 = pd.read_csv(data_schoolagepopulation_englandwales)
    df1.columns=['rowid','msoaiz','count_primary','count_secondary']
    df2 = pd.read_csv(data_schoolagepopulation_scotland)
    df2.columns=['msoaiz','count_primary','count_secondary']
    df3 = df1.append(df2)
    df3.to_csv(data_schoolagepopulation)
    #there, that's nice, england, wales and scotland all back together again

################################################################################
# End initialisation
################################################################################

#Now on to the model run section


#load zone codes lookup file to convert MSOA codes into zone i indexes for the model
#zonecodes = ZoneCodes.fromFile()
zonecodes = pd.read_csv(os.path.join(modelRunsDir,ZoneCodesFilename))
zonecodes.set_index('areakey')

#load cost matrix, time in minutes between MSOA zones
cij = loadQUANTMatrix(os.path.join(modelRunsDir,QUANTCijRoadMinFilename))

#now run the relevant models to produce the outputs
#runRetail()
runSchools()

################################################################################
# END OF MAIN PROGRAM                                                          #
################################################################################

#What follows from here are the different model run functions for retail, schools
#and hospitals


################################################################################
# Retail Model                                                                 #
################################################################################

def runRetail():
    #load income data for MSOA residential zones
    #TODO: this will have to be by age in the next version
    incomeTable = IncomeTable(os.path.join(modelRunsDir,onsModelBasedIncome2011))
    Ei = incomeTable.getEi(zonecodes)

    #load the Geolytix retail points file and make an attraction vector from the floorspace
    retailPoints = loadCSV(data_retailpoints_geocoded)
    Aj = attractions_msoa_floorspace_from_retail_points(zonecodes,retailPoints)

    #calibrate - how?

    m, n = cij.shape
    model = QUANTRetailModel(m,n)
    Sij_a = model.run(1.0,Aj,cij,Ei)
    #TODO: what do you do with the data?

################################################################################


################################################################################
# Schools Model                                                                #
################################################################################

def runSchoolsModel():
    #schools model
    #load primary population
    primaryZones, primaryAttractors = QUANTSchoolsModel.loadSchoolsData(data_schools_ewprimary)
    #print(primaryZones.head())
    #print(primaryAttractors.head())
    row,col = primaryZones.shape
    print("primaryZones count =",row)
    print("primaryZones max = ",primaryZones.max(axis=0))
    primaryZones.to_csv(data_primary_zones)
    primaryAttractors.to_csv(data_primary_attractors)
    primaryPopMSOA = pd.read_csv(data_schoolagepopulation) #[,geography code,count_primary,count_secondary]
    #index code inputs to model by zonecode here to get the two input vectors NOTE: attractors indexed by school ID and population by MSOA
    #primaryAttractors.sort_values(by=['zonei'],inplace=True) #sort by zonei (school id) to give vector in correct order
    #v_primaryAttractors = primaryAttractors['SchoolCapacity'].to_numpy() #that's "schoolcapacity" ordered by zonei
    #print("v_primaryAttractors",v_primaryAttractors) #TODO: you could run a quick check on this to see that it's right
    #v_primaryPopulation = zonecodeIndexData(zonecodes,primaryPopMSOA,"_1","count_primary") #_1 should be "geography code" - why????
    primaryPopulation = primaryPopMSOA.join(other=zonecodes.set_index('areakey'),on='msoaiz')
    #print(primaryPopulation.head())
    primaryPopulation.to_csv(data_primary_population)

    if not os.path.isfile(data_primary_cij):
        primary_cij = costMSOAToPoint(cij,primaryZones) #this takes an hour
        saveMatrix(primary_cij, data_primary_cij)
    else:
        primary_cij = loadMatrix(data_primary_cij)
    m, n = primary_cij.shape
    model = QUANTSchoolsModel(m,n)
    model.setAttractorsAj(primaryAttractors,'zonei','SchoolCapacity')
    model.setPopulationEi(primaryPopulation,'zonei','count_primary')
    model.setCostMatrixCij(primary_cij)
    beta = 0.13 #from the QUANT calibration
    #note: you can also transform the attactors
    #Pij = pupil flows
    start = time.perf_counter()
    #primary_Pij = model.run(beta)
    end = time.perf_counter()
    print("primary school model run elapsed time (secs)=",end-start)
    #cbar = model.computeCBar(primary_Pij,primary_cij)
    #print("cbar=",cbar)
    #cbar=11.208839769105412, beta=0.13 OLD EW S=0
    #cbar= 9.302208987297865, beta=0.2 OLD EW S=0 
    #cbar=24.646849666280524, beta=0.13 NEW EWS
    #cbar= 21.00304170762631, beta=0.2 NEW EWS

    #primary_probPij = model.computeProbabilities(primary_Pij)
    #saveMatrix(primary_probPij,data_primary_probPij)

    ###

    #OK, now on to secondary schools... yes, I know it's bascially the same code
    secondaryZones, secondaryAttractors = QUANTSchoolsModel.loadSchoolsData(data_schools_ewsecondary)
    row,col = secondaryZones.shape
    print("secondaryZones count =",row)
    print("secondaryZones max = ",secondaryZones.max(axis=0))
    secondaryZones.to_csv(data_secondary_zones)
    secondaryAttractors.to_csv(data_secondary_attractors)
    secondaryPopMSOA = pd.read_csv(data_schoolagepopulation)
    secondaryPopulation = secondaryPopMSOA.join(other=zonecodes.set_index('areakey'),on='msoaiz')
    secondaryPopulation.to_csv(data_secondary_population)
    #
    if not os.path.isfile(data_secondary_cij):
        secondary_cij = costMSOAToPoint(cij,secondaryZones) #this takes an hour
        saveMatrix(secondary_cij, data_secondary_cij)
    else:
        secondary_cij = loadMatrix(data_secondary_cij)
    m, n = secondary_cij.shape
    model = QUANTSchoolsModel(m,n)
    model.setAttractorsAj(secondaryAttractors,'zonei','SchoolCapacity')
    model.setPopulationEi(secondaryPopulation,'zonei','count_secondary')
    model.setCostMatrixCij(secondary_cij)
    beta = 0.13
    start = time.perf_counter()
    secondary_Pij = model.run(beta)
    end = time.perf_counter()
    print("secondary school model run elapsed time (secs)=",end-start)
    cbar = model.computeCBar(secondary_Pij,secondary_cij)
    print("cbar=",cbar)
    secondary_probPij = model.computeProbabilities(secondary_Pij)
    saveMatrix(secondary_probPij,data_secondary_probPij)
##


################################################################################


