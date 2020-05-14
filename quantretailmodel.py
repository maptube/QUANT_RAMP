"""
quantretailmodel.py
Build a retail model for QUANT
"""

import numpy as np
from numpy import exp
import pandas as pd

from quantlhmodel import QUANTLHModel

class QUANTRetailModel(QUANTLHModel):
    #test=0

    """
    constructor
    @param n number of residential zones
    @param m number of retail zones
    """
    def __init__(self,m,n):
        #constructor
        super().__init__(m,n)
    #end def constructor

    ################################################################################

    """
    loadGeolytixData
    @param filename Name of file to load - this is the Geolytix restricted access data with
    the floorspace and retail data
    @returns DataFrame containing [key,zonei,east,north] and [zonei,weekly turnover]
    """
    @staticmethod
    def loadGeolytixData(filename):
        missing_values = ['-', 'n/a', 'na', '--', ' -   '] #yes, really, it's space - space space...
        df = pd.read_csv(filename,usecols=['gluid','fascia','modelled sq ft','Weekly TI','bng_e','bng_n'], na_values=missing_values)
        df.dropna(axis=0,inplace=True)
        df.reset_index(drop=True,inplace=True) #IMPORTANT, otherwise indexes remain for ALL the rows i.e. idx=0..OriginalN NOT true row count!
        dfzones = pd.DataFrame({'gluid':df.gluid,'zonei':df.index,'east':df.bng_e,'north':df.bng_n})
        dfattractors = pd.DataFrame({'zonei':df.index,'Weekly TI':df['Weekly TI']}) #could also used floorspace
        print(dfattractors)
        return dfzones, dfattractors

    ################################################################################


#end class