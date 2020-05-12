"""
globals.py

Globals used by model
"""
import os

################################################################################
#setup consts
datadir_ex = "./external-data"
modelRunsDir = "./model-runs"
data_oa_shapefile = os.path.join(datadir_ex, "geography/infuse_oa_lyr_2011_clipped/infuse_oa_lyr_2011_clipped.shp")
data_msoa_shapefile = os.path.join(datadir_ex, "geography/infuse_msoa_lyr_2011_clipped/infuse_msoa_lyr_2011_clipped.shp")
data_geolytix_retailpoints = os.path.join(datadir_ex,"Geolytix/GEOLYTIX - RetailPoints/geolytix_retailpoints_v15_202001.csv")
#data_schools_ewprimary = os.path.join(datadir_ex,"OSF_RAMPUrbanAnalytics/primary_ew.csv")
#data_schools_ewsecondary = os.path.join(datadir_ex,"OSF_RAMPUrbanAnalytics/secondary_ew.csv")
data_schools_ews_primary = os.path.join(datadir_ex,"OSF_RAMPUrbanAnalytics/primary_ews.csv")
data_schools_ews_secondary = os.path.join(datadir_ex,"OSF_RAMPUrbanAnalytics/secondary_ews.csv")
data_census_QS103 = os.path.join(datadir_ex,"Census2011/MSOA/QS103EW_MSOA.csv")
data_census_QS103SC = os.path.join(datadir_ex,"Census2011/MSOA/QS103SC_DZ2001.csv")
lookup_DZ2001_to_IZ2001 = os.path.join(datadir_ex,"Census2011/MSOA/DZ2001Lookup.csv")
#output files
data_retailpoints_geocoded = os.path.join(modelRunsDir,"retailpoints_geocoded.csv")
data_retailpoints_msoa_costs = os.path.join(modelRunsDir,"retailpoints_msoa_Cij_road_min.csv")
data_schoolagepopulation_englandwales = os.path.join(modelRunsDir,"schoolagepopulation_englandwales_msoa.csv")
data_schoolagepopulation_scotland = os.path.join(modelRunsDir,"schoolagepopulation_scotland_iz.csv")
data_schoolagepopulation = os.path.join(modelRunsDir,"schoolagepopulation_englandwalesscotland_msoaiz.csv")
data_primary_cij = os.path.join(modelRunsDir,"primaryCij.bin")
data_primary_zones = os.path.join(modelRunsDir,"primaryZones.csv")
data_primary_attractors = os.path.join(modelRunsDir,"primaryAttractors.csv")
data_primary_population = os.path.join(modelRunsDir,"primaryPopulation.csv")
data_primary_probPij = os.path.join(modelRunsDir,"primaryProbPij.bin")
data_secondary_cij = os.path.join(modelRunsDir,"secondaryCij.bin")
data_secondary_zones = os.path.join(modelRunsDir,"secondaryZones.csv")
data_secondary_attractors = os.path.join(modelRunsDir,"secondaryAttractors.csv")
data_secondary_population = os.path.join(modelRunsDir,"secondaryPopulation.csv")
data_secondary_probPij = os.path.join(modelRunsDir,"secondaryProbPij.bin")
################################################################################
#these are download urls for big external data that can't go in the GitHub repo
url_QUANTCijRoadMinFilename = "https://liveuclac-my.sharepoint.com/:u:/g/personal/ucfnrmi_ucl_ac_uk/EZd4HZVVHd1OuZ_Qj3uKGNcBSe_OoG6unjrVbAyRvGquaQ?e=LxuwMv"
#osf schools
################################################################################

#TravelToWorkFilename = 'wu03ew_msoa.csv'
#ZoneCodesFilename = 'ZoneCodesText.csv'
ZoneCodesFilename = 'EWS_ZoneCodes.csv'

#cost matrix names
QUANTCijRoadMinFilename = 'dis_roads_min.bin'
#QUANTCijBusMinFilename = 'dis_bus_min.bin'
#QUANTCijRailMinFilename = 'dis_gbrail_min.bin'
CijRoadMinFilename = 'Cij_road_min.bin'
#CijBusMinFilename = 'Cij_bus_min.bin'
#CijRailMinFilename = 'Cij_gbrail_min.bin'

#centroids for the cost matrices
QUANTCijRoadCentroidsFilename = 'roadcentroidlookup_QC.csv'

#income
onsModelBasedIncome2011 = 'ons-model-based-income-estimates-msoa_2011-12-weekly-income.csv'
