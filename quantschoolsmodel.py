"""
quantschoolsmodel.py
Build a model for schools.
OK, so we have schools and locations (e.g. east/north) with a pupil capacity.
We have residential MSOA zones with numbers of school age children.
The aim is to make the flow matrix for how many pupils travel from each MSOA to each school.
This is done by guessing the alpha and beta factors... (TBC)
School capacity is used as a constraint.
P=Pupils (residential MSOA x8435)
S=Schools (point x~30000 ?) capacity
Cij=cost matrix at MSOA level (road)

Primary age is 5-11? but KS102 is 5-7 and 8-9 and 10-14! - USE LC1117EW, breakdown is single years
NO - USE QS103 which is age broken down into single years

TODO: ideally, this would JUST be the model, generic with NO SCHOOL RELATED CODE
It's just a Lakshmanan and Hansen form model.
"""

import numpy as np
from numpy import exp
import pandas as pd

class QUANTSchoolsModel:

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
    loadSchoolsData
    Loads the schools data from CSV containing [capacity,east,north]
    EstablishmentStatus_code 1=open, 2=closed
    SchoolCapacity (can be N/A)
    Easting
    Northing
    @param filename Schools file to load (could be primary or secondary)
    @returns DataFrame containing [key,zonei,east,north] and [zonei,capacity] (for just the open schools)
    """
    @staticmethod
    def loadSchoolsData(filename):
        keyFieldName = "EstablishmentNumber"
        openFieldName = "EstablishmentStatus_code"
        capacityFieldName = "SchoolCapacity"
        eastFieldName = "Easting"
        northFieldName = "Northing"
        df = pd.read_csv(filename,usecols=[keyFieldName,openFieldName,capacityFieldName,eastFieldName,northFieldName])
        df = df.dropna(axis=0) #drop the n/a values
        df = df[df[openFieldName] == 1] #drop any school which is not open (i.e. retain==1)
        df.reset_index(drop=True,inplace=True) #IMPORTANT, otherwise indexes remain for the 28,000 or so rows i.e. idx=0..28000! NOT true row count!
        #row,col = df.shape
        #print("primaryZones count =",df)
        #print("primaryZones max = ",df.max(axis=0))

        dfzones = pd.DataFrame({'EstablishmentNumber':df.EstablishmentNumber,'zonei':df.index,'east':df.Easting,'north':df.Northing})
        #dfzones.set_index('EstablishmentNumber')
        dfattractors = pd.DataFrame({'zonei':df.index,'SchoolCapacity':df.SchoolCapacity})

        return dfzones, dfattractors
        #POST: zonecodes for schools = [key,zonei,east,north] and attactor vector = [zonei,capacity]
    #end def

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
    TODO: this is from the retail model
    TODO: this takes rather a long time to run on Python with this amount of data
    @param Beta_a
    PRE: @param Aj
    PRE: @param cij
    PRE: @param Ei_a
    @returns Pij pupil flow
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
        Pij = np.arange(self.m*self.n).reshape(self.m, self.n) #or np.zeros(N*N).reshape(N, N)
        ExpMBetaCij = np.exp(-Beta*self.cij)
        for i in range(self.m):
            #denom = 0
            #for j in range(self.n):
            #    #denom = denom + Aj[j]*exp(-Beta*cij[i,j])
            #    denom = denom + Aj[j] * ExpMBetaCij[i,j]
            denom = np.sum(self.Aj * ExpMBetaCij[i,])
            for j in range(self.n):
                #Pij[i,j] = Ei[i] * (Aj[j]*exp(-Beta*cij[i,j]))/denom
                Pij[i,j] = self.Ei[i] * (self.Aj[j]*ExpMBetaCij[i,j])/denom
        return Pij
    #end def run

    ################################################################################

    """
    computeProbabilities
    Compute the probability of a pupil travelling from an MSOA zone to any (i.e. all)
    of the possible schools.
    @param Pij pupil flows matrix
    @returns probPij, but with each set of MSOA flows to schools scaled to a probability
    """
    def computeProbabilities(self,Pij):
        probPij = np.arange(self.m*self.n).reshape(self.m, self.n)
        for i in range(self.m):
            sum=np.sum(Pij[i,])
            if sum<=0:
                sum=1 #catch for divide by zero - just let the zero probs come through to the final matrix
            probPij[i,]=Pij[i,]/sum
        #end for
        return probPij

    ################################################################################
