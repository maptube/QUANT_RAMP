"""
quantretailmodel.py
Build a retail model for QUANT
"""

import numpy as np
from numpy import exp

class QUANTRetailModel:
    #test=0

    """
    constructor
    @param n number of residential zones
    @param m number of retail zones
    """
    def __init__(self,m,n):
        #constructor
        self.m = m
        self.n = n
    #end def constructor

    ################################################################################

    def calibrate(self):
        #calibrate model
        a=1
    #end def calibrate

    ################################################################################

    """
    run Model run
    TODO: this takes rather a long time to run on Python with this amount of data
    @param Beta_a
    @param Aj
    @param cij
    @param Ei_a
    """
    def run(self, Beta_a, Aj, cij, Ei_a):
        #run model
        #TODO: first attempt, take the age groups out
        #it's really a separate model for each age group
        #a=age group
        #i=residential zone
        #j=shopping centre
        #Eia=expenditure available to shop at residential zone i by age group a
        #Aj=attractor of supermarket
        #Aj=FjLambda where the attractor is +ve power of floorspace
        #cij=travel cost
        #Betaa=scaling param
        Sij_a = np.arange(self.m*self.n).reshape(self.m, self.n) #or np.zeros(N*N).reshape(N, N)
        for i in range(self.m):
            denom = 0
            for j in range(self.n):
                denom = denom + Aj[j]*exp(-Beta_a*cij[i,j])
            for j in range(self.n):
                Sij_a[i,j] = Ei_a[i] * (Aj[j]*exp(-Beta_a*cij[i,j]))/denom
        return Sij_a
    #end def run

    ################################################################################

#end class