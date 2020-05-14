"""
QUANTLHModel.py

Lakshmanan and Hansen form model. Used as a base for other models.
Uses an attractor, Aj, Population Ei and cost matrix Cij.
"""

import numpy as np
from numpy import exp
import pandas as pd

class QUANTLHModel:

    """
    constructor
    @param n number of residential zones (MSOA)
    @param m number of school point zones
    """
    def __init__(self,m,n):
        #constructor
        self.m = m
        self.n = n
        self.Ei = np.zeros(m)
        self.Aj = np.zeros(n)
        self.cij = np.zeros(1) #costs matrix - set to something BIG later
    #end def constructor

    ################################################################################

    """
    setPopulationVectorEi
    Overload of setPopulationEi to set Ei directly from a vector, rather than a Pandas dataframe.
    """
    def setPopulationVectorEi(self,Ei):
        self.Ei = Ei
        assert len(self.Ei)==self.m, "FATAL: setPopulationEi length Ei="+str(len(self.Ei))+" MUST equal model definition size of m="+str(self.m)

    ################################################################################

    """
    setPopulationEi
    Given a data frame containing one column with the zone number (i) and one column
    with the actual data values, fill the Ei population property with data so that
    the position in the Ei numpy array is the zonei field of the data.
    The code is almost identical to the setAttractorsAj method.
    NOTE: max(i) < self.m
    """
    def setPopulationEi(self,df,zoneiColName,dataColName):
        df2=df.sort_values(by=[zoneiColName])
        self.Ei = df2[dataColName].to_numpy()
        assert len(self.Ei)==self.m, "FATAL: setPopulationEi length Ei="+str(len(self.Ei))+" MUST equal model definition size of m="+str(self.m)

    ################################################################################

    """
    setAttractorsAj
    Given a data frame containing one column with the zone number (j) and one column
    with the actual data values, fill the Aj attractors property with data so that
    the position in the Aj numpy array is the zonej field of the data.
    The code is almost identical to the setPopulationEi method.
    NOTE: max(j) < self.n
    """
    def setAttractorsAj(self,df,zonejColName,dataColName):
        df2=df.sort_values(by=[zonejColName])
        self.Aj = df2[dataColName].to_numpy()
        assert len(self.Aj)==self.n, "FATAL: setAttractorsAj length Aj="+str(len(self.Aj))+" MUST equal model definition size of n="+str(self.n)

    ################################################################################

    """
    setCostsMatrix
    Assign the cost matrix for the model to use when it runs.
    NOTE: this MUST match the m x n order of the model and be a numpy array
    """
    def setCostMatrixCij(self,cij):
        i, j = cij.shape
        assert i==self.m, "FATAL: setCostsMatrix cij matrix is the wrong size, cij.m="+str(i)+" MUST match model definition of m="+str(self.m)
        assert j==self.n, "FATAL: setCostsMatrix cij matrix is the wrong size, cij.n="+str(j)+" MUST match model definition of n="+str(self.n)
        self.cij=cij
    
    ################################################################################

    """
    computeCBar
    Compute average trip length TODO: VERY COMPUTATIONALLY INTENSIVE - FIX IT
    @param Sij trips matrix containing the flow numbers between MSOA (i) and schools (j)
    @param cij trip times between i and j
    """
    @staticmethod
    def computeCBar(Sij,cij):
        sum=0
        denom=0
        m,n = Sij.shape
        for i in range(m):
            for j in range(n):
                sum+=Sij[i,j]*cij[i,j]
                denom+=Sij[i,j]
        cbar = sum/denom
        return cbar

    ################################################################################


    """
    run Model run
    TODO: this is from the retail model
    TODO: this takes rather a long time to run on Python with this amount of data
    @param Beta_a
    PRE: @param Aj
    PRE: @param cij
    PRE: @param Ei_a
    @returns Sij predicted flows between i and j
    """
    def run(self, Beta):
        #run model
        #i=residential zone
        #j=school
        #Ei=Pupils available at MSOA location
        #Aj=attractor of school
        #Aj=FjLambda where the attractor is +ve power of floorspace (from retail model)
        #cij=travel cost
        #Beta=scaling param
        Sij = np.arange(self.m*self.n,dtype=np.float).reshape(self.m, self.n) #or np.zeros(N*N).reshape(N, N)
        ExpMBetaCij = np.exp(-Beta*self.cij)
        for i in range(self.m):
            #denom = 0
            #for j in range(self.n):
            #    #denom = denom + Aj[j]*exp(-Beta*cij[i,j])
            #    denom = denom + Aj[j] * ExpMBetaCij[i,j]
            denom = np.sum(self.Aj * ExpMBetaCij[i,])
            for j in range(self.n):
                #Sij[i,j] = Ei[i] * (Aj[j]*exp(-Beta*cij[i,j]))/denom
                Sij[i,j] = self.Ei[i] * (self.Aj[j]*ExpMBetaCij[i,j])/denom
        return Sij
    #end def run

    ################################################################################

    """
    computeProbabilities
    Compute the probability of a flow from an MSOA zone to any (i.e. all)
    of the possible point zones.
    @param Sij flows matrix
    @returns probSij, but with each set of MSOA flows to schools scaled to a probability
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
