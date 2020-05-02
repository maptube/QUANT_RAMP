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
#output files
data_retailpoints_geocoded = os.path.join(modelRunsDir,"retailpoints_geocoded.csv")
data_retailpoints_msoa_costs = os.path.join(modelRunsDir,"retailpoints_msoa_Cij_road_min.csv")
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
