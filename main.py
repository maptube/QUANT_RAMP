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
from databuilder import geolytixRegression, geolytixOpenDataRegression, geocodeGeolytix, computeGeolytixCosts
from databuilder import buildSchoolsPopulationTableEnglandWales, buildSchoolsPopulationTableScotland
from databuilder import buildTotalPopulationTable
from databuilder import matchHospitalEpisodeData
from incometable import IncomeTable
from attractions import attractions_msoa_floorspace_from_retail_points
from quantretailmodel import QUANTRetailModel
from quantschoolsmodel import QUANTSchoolsModel
from quanthospitalsmodel import QUANTHospitalsModel
from quantsingleorigin import SingleOrigin
from quantsingledestination import SingleDestination
from costs import costMSOAToPoint
from analytics import runAnalytics

################################################################################
# Initialisation                                                               #
################################################################################

#NOTE: this section provides the base data for the models that come later. This
#will only be run on the first run of the program to assemble all the tables
#required from the original sources. After that, if the file exists in the
#directory, then nothing new is created and this section is effectively
#skipped, up until the model run section at the end.

#make a model-runs dir if we need it
if not os.path.exists(modelRunsDir):
    os.makedirs(modelRunsDir)

#Downloads first:

#this will get us the big QUANT road travel times matrix
ensureFile(os.path.join(modelRunsDir,QUANTCijRoadMinFilename),url_QUANTCijRoadMinFilename)
ensureFile(os.path.join(modelRunsDir,ZoneCodesFilename),url_QUANT_ZoneCodes) #and the zone code lookup that goes with it
ensureFile(os.path.join(modelRunsDir,QUANTCijRoadCentroidsFilename),url_QUANT_RoadCentroids) #and the road centroids

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
#if not os.path.isfile(data_restricted_geolytix_regression):
#    geolytixRegression(data_restricted_geolytix_supermarketattractivenenss,data_geolytix_retailpoints,data_restricted_geolytix_regression)

#This is the open data version of the above restricted data regression - uses linear regression params derived from the above data that we can't release
if not os.path.isfile(data_open_geolytix_regression):
    geolytixOpenDataRegression(data_geolytix_retailpoints,data_open_geolytix_regression)


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
    #retailZones, retailAttractors = QUANTRetailModel.loadGeolytixData(data_restricted_geolytix_regression) #this is the restricted data
    retailZones, retailAttractors = QUANTRetailModel.loadGeolytixData(data_open_geolytix_regression) #and this is the open data
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
Alternative hospitals model based on age group admissions.
Predict actual number of people in each age group going to each hospital.
PRE: requires data_agepopulation
"""
def runAgeHospitalsModel():
    print("not implemented")
    #buildTotalPopulationTable() #should have already been done by the installer

    dfMSOAAges = pd.read_csv(data_agepopulation,dtype={
        'date':'string', 'geography':'string', 'msoaiz':'string', 'All people':float,
        'Under 1':float, '1':float, '2':float, '3':float, '4':float, '5':float, '6':float, '7':float, '8':float, '9':float,
        '10':float, '11':float, '12':float, '13':float, '14':float, '15':float, '16':float, '17':float, '18':float, '19':float,
        '20':float, '21':float, '22':float, '23':float, '24':float, '25':float, '26':float, '27':float, '28':float, '29':float,
        '30':float, '31':float, '32':float, '33':float, '34':float, '35':float, '36':float, '37':float, '38':float, '39':float,
        '40':float, '41':float, '42':float, '43':float, '44':float, '45':float, '46':float, '47':float, '48':float, '49':float,
        '50':float, '51':float, '52':float, '53':float, '54':float, '55':float, '56':float, '57':float, '58':float, '59':float,
        '60':float, '61':float, '62':float, '63':float, '64':float, '65':float, '66':float, '67':float, '68':float, '69':float,
        '70':float, '71':float, '72':float, '73':float, '74':float, '75':float, '76':float, '77':float, '78':float, '79':float,
        '80':float, '81':float, '82':float, '83':float, '84':float, '85':float, '86':float, '87':float, '88':float, '89':float,
        '90':float, '91':float, '92':float, '93':float, '94':float, '95':float, '96':float, '97':float, '98':float, '99':float,
        '100 and over':float, 'count_allpeople':float
        }) #need zonei!
    dfMSOAAges = dfMSOAAges.join(other=zonecodes.set_index('areakey'),on='msoaiz') #zone with the zone codes to add zonei col
    dfHospitalAges = pd.read_csv(data_hospitalAges,na_values = ['NA'])
    dfHospitalAges.fillna(0, inplace=True)

    #make the zones from the raw data
    dfHospitalZones = pd.DataFrame({'id':dfHospitalAges['SiteAndTrustCode'],'name':dfHospitalAges['Name'],
        'zonei':dfHospitalAges.index,'east':dfHospitalAges.oseast1m,'north':dfHospitalAges.osnrth1m})

    #hospital admission fields to msoa age fields - every one is a model
    modeldefs = {
        'Age 0' : ['Under 1'],
        'Age 1-4' : ['1','2','3','4'],
        'Age 5-9' : ['5','6','7','8','9'],
        'Age 10-14' : ['10','11','12','13','14'],
        'Age 15' : ['15'],
        'Age 16' : ['16'],
        'Age 17' : ['17'],
        'Age 18' : ['18'],
        'Age 19' : ['19'],
        'Age 20-24' : ['20','21','22','23','24'],
        'Age 25-29' : ['25','26','27','28','29'],
        'Age 30-34' : ['30','31','32','33','34'],
        'Age 35-39' : ['35','36','37','38','39'],
        'Age 40-44' : ['40','41','42','43','44'],
        'Age 45-49' : ['45','46','47','48','49'],
        'Age 50-54' : ['50','51','52','53','54'],
        'Age 55-59' : ['55','56','57','58','59'],
        'Age 60-64' : ['60','61','62','63','64'],
        'Age 65-69' : ['65','66','67','68','69'],
        'Age 70-74' : ['70','71','72','73','74'],
        'Age 75-79' : ['75','76','77','78','79'],
        'Age 80-84' : ['80','81','82','83','84'],
        'Age 85-89' : ['85','86','87','88','89'],
        'Age 90+' : ['90','91','92','93','94','95','96','97','98','99','100 and over']
    }

    #then Destinations are the hospital admissions (by age)
    #Age 0, Age 1-4, Age 5-9, Age 10-14, Age 15, Age 16, Age 17, Age 18, Age 19, Age 20-24, Age 25-29, Age 30-34, Age 35-39, Age 40-44, Age 45-49, Age 50-54, Age 55-59, Age 60-64, Age 65-69, Age 70-74, Age 75-79, Age 80-84, Age 85-89, Age 90+
    #NOTE: this is slightly weird - I'm basically taking the hospital age admisions table and copying it into the Dj table while adding
    #the zonei join on the hospitals key. You could just use the original table and drop out all the extra fields, but this makes a lot
    #more sense as the content of the Dj table is controlled by the model defs above i.e. it's easy to change the model defs
    dfHospitalAgesDj = pd.DataFrame({'zonei':dfHospitalAges.index,'Name':dfHospitalAges.Name}) #it's always zonei, even if it's j
    for key in modeldefs:
        dfHospitalAgesDj[key] = dfHospitalAges[key]
    dfHospitalAgesDj.to_csv(data_hospitalAges_Dj,index=False)

    #and the Origins are the MSOA population counts (by age), grouped according to the hospital defintions
    dfHospitalAgesOi = pd.DataFrame({'zonei':dfMSOAAges.zonei, 'msoaiz':dfMSOAAges.msoaiz})
    for key, fields in modeldefs.items():
        dfHospitalAgesOi[key]=dfMSOAAges[fields[0]] #I'm sure there's a better way of adding all the modeldefs fields together
        for i in range(1,len(fields)):
            dfHospitalAgesOi[key]+=dfMSOAAges[fields[i]]
        #end for
    #end for
    dfHospitalAgesOi.to_csv(data_hospitalAges_Oi,index=False)

    #make or load Cij
    if not os.path.isfile(data_hospitalAges_cij):
        hospitalAges_cij = costMSOAToPoint(cij,dfHospitalZones) #this takes an hour
        saveMatrix(hospitalAges_cij, data_hospitalAges_cij)
    else:
        hospitalAges_cij = loadMatrix(data_hospitalAges_cij)

    #that's the data, now on to the model
    m, n = hospitalAges_cij.shape
    #model = SingleOrigin(m,n)
    model = SingleDestination(m,n)
    model.setOi(dfHospitalAgesOi,'zonei','Age 45-49')
    model.setDj(dfHospitalAgesDj,'zonei','Age 45-49')
    model.setCostMatrixCij(hospitalAges_cij)
    model.run()
    #and maybe do something with the flow matrix output here?


################################################################################


################################################################################
#Now on to the model run section
################################################################################


#load zone codes lookup file to convert MSOA codes into zone i indexes for the model
#zonecodes = ZoneCodes.fromFile()
zonecodes = pd.read_csv(os.path.join(modelRunsDir,ZoneCodesFilename))
zonecodes.set_index('areakey')

#load cost matrix, time in minutes between MSOA zones
#cij = loadQUANTMatrix(os.path.join(modelRunsDir,QUANTCijRoadMinFilename))

#now run the relevant models to produce the outputs
#runRetailModel()
#runSchoolsModel()
#runHospitalsModel()

##new models
#runPopulationRetailModel()

################################################################################
#analytics - let's see how well it works                                       #
################################################################################

runAnalytics()


################################################################################

#DEBUG
#matchHospitalEpisodeData()
#geocodeHospitalEpisodeData(
#    os.path.join(datadir_ex,'NSPL_FEB_2019_UK/Data/NSPL_FEB_2019_UK.csv'),
#    os.path.join(datadir_ex,'Hospitals2/hospital_providers_and_18_19_patient_counts.csv'),
#    os.path.join(datadir_ex,'Hospitals2/hospital_providers_and_18_19_patient_counts_geocoded.csv'))

#runAgeHospitalsModel()

################################################################################
# END OF MAIN PROGRAM                                                          #
################################################################################


