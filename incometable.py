"""
incometable.py
Build a table of income by MSOA by age for use in the model
"""

import numpy as np
import csv

class IncomeTable:

    def __init__(self,weeklyIncomeFilename):
        self.incomeByMSOA = {} #hash keyed on MSOA containing weekly income
        self.loadONSModelBasedIncome(weeklyIncomeFilename)

    ################################################################################

    """
    loadONSModelBasedIncome
    @param filename the name of the ONS information containing the modelled income by MSOA code
    load a csv file containing income estimates for weekly income for each zone (MSOA)
    data here:
    https://data.london.gov.uk/dataset/ons-model-based-income-estimates--msoa

    expecting:
    MSOA code,MSOA name,Local authority code,Local authority name,Region code,Region name,Total weekly income (£),Upper confidence limit (£),Lower confidence limit (£),Confidence interval (£),Net weekly income (£),Upper confidence limit (£),Lower confidence limit (£),Confidence interval (£),Net income before housing costs (£),Upper confidence limit (£),Lower confidence limit (£),Confidence interval (£),Net income after housing costs (£),Upper confidence limit (£),Lower confidence limit (£),Confidence interval (£)
    E02004297,County Durham 001,E06000047,County Durham,E12000001,North East,630,690,570,120,480,520,440,80,480,530,440,90,450,510,390,120
    E02004290,County Durham 002,E06000047,County Durham,E12000001,North East,730,800,660,140,540,590,500,90,510,560,460,100,460,530,400,120

    NOTE: this does NOT have any age information, so we're going to need a second piece of data to produce that
    """
    def loadONSModelBasedIncome(self,filename):
        self.incomeByMSOA = {}
        with open(filename, newline = '') as csvFile:
            reader = csv.reader(csvFile,delimiter=',',quotechar='"')
            next(reader) #skip header row
            for row in reader:
                msoaCode = row[0]
                netIncomeAfterHousing = float(row[18])
                self.incomeByMSOA[msoaCode] = netIncomeAfterHousing
            #end for
        #end with
    #end def

    ################################################################################

    """
    getEi The main use of this class - get a vector of income data for use in the model
    @param zonecodes the dataframe object containing the zone data linking the MSOA code to the zone i number
    @returns a vector of income, one for each MSOA, suitable for using in the model

    """
    def getEi(self,zonecodes):
        N = len(zonecodes)
        Ei = np.zeros(N,dtype=float)
        for msoa in self.incomeByMSOA:
            income = self.incomeByMSOA[msoa]
            zonei = zonecodes.loc[zonecodes['areakey'] == msoa, 'zonei'].values[0]
            Ei[zonei]=income
        #end for
        return Ei
    #end def getEi

    ################################################################################

    """
    TODO:
    getEi_age
    The idea is that this is like getEi, but returns data weighted by some age distribution
    HOW????
    """
    def __getEi_age(self):
        print("NOT IMPLEMENTED")

    ################################################################################

