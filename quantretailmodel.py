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

    """
    computeCBar
    Compute average trip length TODO: VERY COMPUTATIONALLY INTENSIVE - FIX IT
    @param Pij trips matrix containing the flow numbers between MSOA (i) and schools (j)
    @param cij trip times between i and j
    """
    @staticmethod
    def computeCBar(Pij,cij):
        sum=0
        denom=0
        m,n = Pij.shape
        for i in range(m):
            for j in range(n):
                sum+=Pij[i,j]*cij[i,j]
                denom+=Pij[i,j]
        cbar = sum/denom
        return cbar

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

    """
    computeProbabilities
    Compute the probability of a person travelling from a retail zone to all retail points
    @param Sij retail flows matrix
    @returns probSij, but with each set of MSOA flows to retail scaled to a probability
    """
    def computeProbabilities(self,Sij):
        probSij = np.arange(self.m*self.n,dtype=np.float).reshape(self.m, self.n)
        for i in range(self.m):
            sum=np.sum(Sij[i,])
            if sum<=0:
                sum=1 #catch for divide by zero - just let the zero probs come through to the final matrix
            probSij[i,]=Sij[i,]/sum
        #end for
        return probSij

    ################################################################################


#end class