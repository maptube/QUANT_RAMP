"""
QUANT_RAMP
main.py
"""

import os
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from shapely.strtree import STRtree
import csv

from globals import *
from utils import loadQUANTMatrix, loadCSV
from zonecodes import ZoneCodes
from databuilder import geocodeGeolytix, computeGeolytixCosts
from incometable import IncomeTable
from attractions import attractions_msoa_floorspace_from_retail_points
from quantretailmodel import QUANTRetailModel

#databuilder.py - run the code there...
if not os.path.isfile(data_retailpoints_geocoded):
    geocodeGeolytix()

#make geolytix costs file which is a csv of origin to destination zone with a cost
computeGeolytixCosts()

#load zone codes lookup file to convert MSOA codes into zone i indexes for the model
zonecodes = ZoneCodes.fromFile()

#load cost matrix, time in minutes between MSOA zones
cij = loadQUANTMatrix(os.path.join(modelRunsDir,QUANTCijRoadMinFilename))

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