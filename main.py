"""
QUANT_RAMP
main.py

27 May 2020
Author: Richard Milton, Centre for Advanced Spatial Analysis, University College London
https://www.casa.ucl.ac.uk
Funded by the Alan Turing Institute for Data Science and Artificial Intelligence
https://www.turing.ac.uk/

Repository: https://github.com/maptube/QUANT_RAMP
Licence: read the licence file.

This project was written for the RAMP Covid 19 effort to create a model of probabilities
for visitors to point locations originating from MSOA zones. All data relating to the
population comes from the 2011 census e.g. age structure and financial data. The point
locations are taken to be retail, primary schools, secondary schools or hospitals.
This model is an MSOA zone to point location model based on CASA and the Alan Turing
Institute's QUANT2 model.
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
from utils import loadQUANTMatrix, loadMatrix, saveMatrix, zonecodeIndexData
from zonecodes import ZoneCodes
from databuilder import ensureFile, changeGeography
from databuilder import geolytixRegression, geocodeGeolytix, computeGeolytixCosts
from databuilder import buildSchoolsPopulationTableEnglandWales, buildSchoolsPopulationTableScotland
from databuilder import buildTotalPopulationTable
from databuilder import matchHospitalEpisodeData
from incometable import IncomeTable
from attractions import attractions_msoa_floorspace_from_retail_points
from quantretailmodel import QUANTRetailModel
from quantschoolsmodel import QUANTSchoolsModel
from quanthospitalsmodel import QUANTHospitalsModel
from costs import costMSOAToPoint

################################################################################
# Initialisation                                                               #
################################################################################

#NOTE: this section provides the base data for the models that come later. This
#will only be run on the first run of the program to assemble all the tables
#required from the original sources. After that, if the file exists in the
#directory, then nothing new is created and this section is effectively
#skipped, up until the model run section at the end.

#Downloads first:

#this will get us the big QUANT road travel times matrix
ensureFile(os.path.join(modelRunsDir,QUANTCijRoadMinFilename),url_QUANTCijRoadMinFilename)

#todo: geolytics?
#todo: osf schools data

################################################################################
#Now on to file creation

#databuilder.py - run the code there...
#NOT NEEDED - this was the old Geolytix file, which was geocoded to nearest MSOA and OA zone
#if not os.path.isfile(data_retailpoints_geocoded):
#    geocodeGeolytix()

#make geolytix costs file which is a csv of origin to destination zone with a cost
#computeGeolytixCosts()

#databuilder.py - use regression to add floorspace data and regression turnover data to the open Geolytix data
#NOTE: the result of dong this is the regression file, which contains RESTRICTED Geolytix data and so is
#itself RESTRICTED DATA!
if not os.path.isfile(data_restricted_geolytix_regression):
    geolytixRegression(data_restricted_geolytix_supermarketattractivenenss,data_geolytix_retailpoints,data_restricted_geolytix_regression)

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

#same thing for the total population of England, Scotland and Wales - needed for hospitals
#now join total population for England/Wales and Scotland files together
if not os.path.isfile(data_totalpopulation):
    buildTotalPopulationTable()


###
#Scotland IZ2011 to IZ2005 mapping
#changeGeography(
#    'external-data/geography/SG_DataZoneBdry_2011/SG_DataZone_Bdry_2011.shp',
#    'DataZone',
#    'external-data/geography/Scotland_IZ_2005Release/IZ_2011_EoR_Scotland.shp',
#    'msoa_iz',
#    'external-data/Census2011Modelled/SmallAreaIncomeEstimatesScotland.csv',
#    '2011 Data Zone code',
#    'Median Gross Household Income per week'
#    )
###

################################################################################
# End initialisation
################################################################################


#What follows from here are the different model run functions for retail, schools
#and hospitals


################################################################################
# Retail Model                                                                 #
################################################################################

def runRetailModel():
    #load income data for MSOA residential zones
    #TODO: this will have to be by age in the next version
    #incomeTable = IncomeTable(os.path.join(modelRunsDir,onsModelBasedIncome2011))
    #Ei = incomeTable.getEi(zonecodes)
    #Aj = attractions_msoa_floorspace_from_retail_points(zonecodes,retailPoints) #OLD MODEL

    dfEi = pd.read_csv(data_ewsModelBasedIncome)
    retailPopulation = dfEi.join(other=zonecodes.set_index('areakey'),on='msoaiz') #this codes dfEi by zonei
    retailPopulation.to_csv(data_retailpoints_population)

    #load the Geolytix retail points file and make an attraction vector from the floorspace
    #retailPoints = loadCSV(data_retailpoints_geocoded)
    retailZones, retailAttractors = QUANTRetailModel.loadGeolytixData(data_restricted_geolytix_regression)
    retailZones.to_csv(data_retailpoints_zones)
    retailAttractors.to_csv(data_retailpoints_attractors)

    if not os.path.isfile(data_retailpoints_cij):
        retailpoints_cij = costMSOAToPoint(cij,retailZones) #this takes a while
        saveMatrix(retailpoints_cij, data_retailpoints_cij)
    else:
        retailpoints_cij = loadMatrix(data_retailpoints_cij)
    
    m, n = retailpoints_cij.shape
    model = QUANTRetailModel(m,n)
    model.setAttractorsAj(retailAttractors,'zonei','Modelled turnover annual')
    #model.setPopulationVectorEi(Ei) #note overload to set Ei directly from the IncomeTable vector
    model.setPopulationEi(retailPopulation,'zonei','Total weekly income (£)')
    model.setCostMatrixCij(retailpoints_cij)
    beta = 0.13 #from the QUANT calibration

    start = time.perf_counter()
    Sij = model.run(beta)
    end = time.perf_counter()
    print("retail points model run elapsed time (secs)=",end-start)
    cbar = model.computeCBar(Sij,retailpoints_cij)
    print("cbar=",cbar)

    retailpoints_probSij = model.computeProbabilities(Sij)
    saveMatrix(retailpoints_probSij,data_retailpoints_probSij)

################################################################################

"""
runPopulationRetailModel
Same as runRetailModel, except that it now uses number of people in place of average income
"""
def runPopulationRetailModel():
    dfPopMSOAPopulation = pd.read_csv(data_totalpopulation,usecols=['msoaiz','count_allpeople'])
    popretailPopulation = dfPopMSOAPopulation.join(other=zonecodes.set_index('areakey'),on='msoaiz') #join with the zone codes to add zonei col
    popretailPopulation.to_csv(data_populationretail_population)

    #load the Geolytix retail points file and make an attraction vector from the floorspace - copied from runRetailModel
    popretailZones, popretailAttractors = QUANTRetailModel.loadGeolytixData(data_restricted_geolytix_regression)
    popretailZones.to_csv(data_populationretail_zones) #NOTE: saving largely for data completeness - these two are identical to the retail points model of income
    popretailAttractors.to_csv(data_populationretail_attractors)

    if not os.path.isfile(data_retailpoints_cij):
        print("ERROR! need to run runRetailModel first to generate Cij costs")
    else:
        retailpoints_cij = loadMatrix(data_retailpoints_cij) #NOTE: this is the retailpoints cij costs which I am NOT going to duplicate as it's BIG!

    #so it's a retail model with poulation instead of income for Ei, then retail zones, attractors and cij are identical
    #here we go with the model then...

    m, n = retailpoints_cij.shape
    model = QUANTRetailModel(m,n)
    model.setAttractorsAj(popretailAttractors,'zonei','Modelled turnover annual')
    model.setPopulationEi(popretailPopulation,'zonei','count_allpeople')
    model.setCostMatrixCij(retailpoints_cij)
    beta = 0.13 #from the QUANT calibration

    start = time.perf_counter()
    Sij = model.run(beta)
    end = time.perf_counter()
    print("retail points model run elapsed time (secs)=",end-start)
    cbar = model.computeCBar(Sij,retailpoints_cij)
    print("cbar=",cbar)

    popretail_probSij = model.computeProbabilities(Sij)
    saveMatrix(popretail_probSij,data_populationretail_probSij)


################################################################################


################################################################################
# Schools Model                                                                #
################################################################################

def runSchoolsModel():
    print("runSchoolsModel running primary schools")
    #schools model
    #load primary population
    primaryZones, primaryAttractors = QUANTSchoolsModel.loadSchoolsData(data_schools_ews_primary)
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
    primary_Pij = model.run(beta)
    end = time.perf_counter()
    print("primary school model run elapsed time (secs)=",end-start)
    cbar = model.computeCBar(primary_Pij,primary_cij)
    print("cbar=",cbar)
    #cbar=11.208839769105412, beta=0.13 OLD EW S=0
    #cbar= 9.302208987297865, beta=0.2 OLD EW S=0 
    #cbar=24.646849666280524, beta=0.13 NEW EWS
    #cbar= 21.00304170762631, beta=0.2 NEW EWS
    ##
    #cbar= 16.430355812412476, beta=0.13 CORRECT EWS

    primary_probPij = model.computeProbabilities(primary_Pij)
    saveMatrix(primary_probPij,data_primary_probPij)

    ###

    #OK, now on to secondary schools... yes, I know it's basically the same code
    print("runSchoolsModel running secondary schools")
    secondaryZones, secondaryAttractors = QUANTSchoolsModel.loadSchoolsData(data_schools_ews_secondary)
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
    #cbar= 16.5250843880515, beta=0.13 correct EWS
##

################################################################################


################################################################################
# Hospitals Model                                                              #
################################################################################

def runHospitalsModel():
    print("runHospitalsModel")
    #hospitals model
    #load hospitals population
    hospitalZones, hospitalAttractors = QUANTHospitalsModel.loadHospitalsData(data_hospitals)
    row,col = hospitalZones.shape
    print("hospitalZones count =",row)
    print("hospitalZones max = ",hospitalZones.max(axis=0))
    hospitalZones.to_csv(data_hospital_zones)
    hospitalAttractors.to_csv(data_hospital_attractors)
    hospitalPopMSOA = pd.read_csv(data_totalpopulation,usecols=['msoaiz','count_allpeople']) #this is the census total count of people
    #print(hospitalPopMSOA.head())
    hospitalPopulation = hospitalPopMSOA.join(other=zonecodes.set_index('areakey'),on='msoaiz') #zone with the zone codes to add zonei col
    #print(hospitalPopulation.head())
    hospitalPopulation.to_csv(data_hospital_population)

    if not os.path.isfile(data_hospital_cij):
        hospital_cij = costMSOAToPoint(cij,hospitalZones) #this takes an hour
        saveMatrix(hospital_cij, data_hospital_cij)
    else:
        hospital_cij = loadMatrix(data_hospital_cij)
    m, n = hospital_cij.shape
    model = QUANTHospitalsModel(m,n)
    model.setAttractorsAj(hospitalAttractors,'zonei','floor_area_m2')
    model.setPopulationEi(hospitalPopulation,'zonei','count_allpeople')
    model.setCostMatrixCij(hospital_cij)
    beta = 0.13 #from the QUANT calibration
    #note: you can also transform the attactors
    #Hij = hospital flows
    start = time.perf_counter()
    hospital_Hij = model.run(beta)
    end = time.perf_counter()
    print("hospitals school model run elapsed time (secs)=",end-start)
    cbar = model.computeCBar(hospital_Hij,hospital_cij)
    print("cbar=",cbar)

    hospital_probHij = model.computeProbabilities(hospital_Hij)
    saveMatrix(hospital_probHij,data_hospital_probHij)


################################################################################

"""
Alternative hospitals model based on age group admissions
"""
def runAgeHospitalsModel():
    print("not implemented")



################################################################################


################################################################################
#Now on to the model run section
################################################################################


#load zone codes lookup file to convert MSOA codes into zone i indexes for the model
#zonecodes = ZoneCodes.fromFile()
zonecodes = pd.read_csv(os.path.join(modelRunsDir,ZoneCodesFilename))
zonecodes.set_index('areakey')

#load cost matrix, time in minutes between MSOA zones
cij = loadQUANTMatrix(os.path.join(modelRunsDir,QUANTCijRoadMinFilename))
print('cij0,0',cij[0,0])
print("cij0,1",cij[0,1])
print("cij1,0",cij[1,0])

#now run the relevant models to produce the outputs
#runRetailModel()
#runSchoolsModel()
#runHospitalsModel()

##new models
#runPopulationRetailModel()

#DEBUG
#matchHospitalEpisodeData()

################################################################################
# END OF MAIN PROGRAM                                                          #
################################################################################


