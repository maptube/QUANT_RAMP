"""
quanthospitalsmodel.py
Build a travel to hospitals model for QUANT
"""

import numpy as np
from numpy import exp
import pandas as pd

from quantlhmodel import QUANTLHModel

class QUANTHospitalsModel(QUANTLHModel):
    #test=0

    """
    constructor
    @param n number of residential zones
    @param m number of hospital zones
    """
    def __init__(self,m,n):
        #constructor
        super().__init__(m,n)
    #end def constructor

    ################################################################################

    """
    loadHospitalsData
    @param filename Name of file to load - this is the NHS dataset containing the hospital locations and numbers of beds
    @returns DataFrame containing [key,zonei,east,north] and [zonei,beds]
    """
    @staticmethod
    def loadHospitalsData(filename):
        missing_values = ['-', 'n/a', 'na', '--', ' -   '] #yes, really, it's space - space space...
        df = pd.read_csv(filename,usecols=['Site Code','Site Name','Occupied floor area (m2)','oseast1m','osnrth1m'], na_values=missing_values)
        df.dropna(axis=0,inplace=True)
        df.reset_index(drop=True,inplace=True) #IMPORTANT, otherwise indexes remain for ALL the rows i.e. idx=0..OriginalN NOT true row count!
        dfzones = pd.DataFrame({'id':df['Site Code'],'name':df['Site Name'],'zonei':df.index,'east':df.oseast1m,'north':df.osnrth1m})
        dfattractors = pd.DataFrame({'zonei':df.index,'floor_area_m2':df['Occupied floor area (m2)']})
        #print(dfattractors)
        return dfzones, dfattractors

    ################################################################################


#end class