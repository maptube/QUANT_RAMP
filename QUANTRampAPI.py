"""
Public interface to the data
Contains accessor functions for getting probabilities of trips from MSOA or IZ origins to
primary schools, secondary schools and retail locations.
Further information is contained in each function description.
"""

import pandas as pd
import pickle

################################################################################
# Utilities
################################################################################


"""
Load a numpy matrix from a file
"""
def loadMatrix(filename):
    with open(filename,'rb') as f:
        matrix = pickle.load(f)
    return matrix

################################################################################
# Globals
################################################################################

dfPrimaryPopulation = pd.read_csv('model-runs/primaryPopulation.csv')
dfPrimaryZones = pd.read_csv('model-runs/primaryZones.csv')
primary_probPij = loadMatrix('model-runs/primaryProbPij.bin')
dfSecondaryPopulation = pd.read_csv('model-runs/secondaryPopulation.csv')
dfSecondaryZones = pd.read_csv('model-runs/secondaryZones.csv')
secondary_probPij = loadMatrix('model-runs/secondaryProbPij.bin')
#onsModelBasedIncome2011
dfRetailPointsZones = pd.read_csv('model-runs/retailpointsZones.csv')
retailpoints_probSij = loadMatrix('model-runs/retailpointsProbSij.bin')


################################################################################
# Interface
################################################################################


"""
getProbablePrimarySchoolsByMSOAIZ
Given an MSOA area code (England and Wales) or an Intermediate Zone (IZ) 2001 code (Scotland), return
a list of all the surrounding primary schools whose probabilty of being visited by the MSOA_IZ is
greater than or equal to the threshold.
School ids are taken from the Edubase list of URN
NOTE: code identical to the secondary school version, only with switched lookup tables
@param msoa_iz An MSOA code (England/Wales e.g. E02000001) or an IZ2001 code (Scotland e.g. S02000001)
@param threshold Probability threshold e.g. 0.5 means return all possible schools with probability>=0.5
@returns a list of [ {id: 'schoolid1', p: 0.5}, {id: 'schoolid2', p:0.6}, ... etc] (NOTE: not sorted in any particular order)
"""
def getProbablePrimarySchoolsByMSOAIZ(msoa_iz,threshold):
    result = []
    zonei = int(dfPrimaryPopulation.loc[dfPrimaryPopulation['msoaiz'] == msoa_iz,'zonei'])
    m,n = primary_probPij.shape
    sum=0
    max=0
    for j in range(n):
        p = primary_probPij[zonei,j]
        sum+=p
        if p>max:
            max=p
        if p>=threshold:
            row2 = dfPrimaryZones.loc[dfPrimaryZones['zonei'] == j] #yes, zonei==j is correct, they're always called 'zonei'
            id = row2['URN'].values[0]
            result.append({'id':id, 'p':p})
        #end if
    #end for
    mean=sum/n
    print("sum=",sum,"max=",max,"mean=",mean)
    return result

################################################################################

"""
getProbableSecondarySchoolsByMSOAIZ
Given an MSOA area code (England and Wales) or an Intermediate Zone (IZ) 2001 code (Scotland), return
a list of all the surrounding secondary schools whose probabilty of being visited by the MSOA_IZ is
greater than or equal to the threshold.
School ids are taken from the Edubase list of URN
NOTE: code identical to the primary school version, only with switched lookup tables
@param msoa_iz An MSOA code (England/Wales e.g. E02000001) or an IZ2001 code (Scotland e.g. S02000001)
@param threshold Probability threshold e.g. 0.5 means return all possible schools with probability>=0.5
@returns a list of [ {id: 'schoolid1', p: 0.5}, {id: 'schoolid2', p:0.6}, ... etc] (NOTE: not sorted in any particular order)
"""
def getProbableSecondarySchoolsByMSOAIZ(msoa_iz,threshold):
    result = []
    zonei = int(dfSecondaryPopulation.loc[dfSecondaryPopulation['msoaiz'] == msoa_iz, 'zonei'])
    m,n = secondary_probPij.shape
    for j in range(n):
        p = secondary_probPij[zonei,j]
        if p>=threshold:
            row2 = dfSecondaryZones.loc[dfSecondaryZones['zonei'] == j] #yes, zonei==j is correct, they're always called 'zonei'
            id = row2['URN'].values[0]
            result.append({'id':id, 'p':p})
        #end if
    #end for
    return result

################################################################################

"""
getProbableSecondarySchoolsByMSOAIZ
Given an MSOA area code (England and Wales) or an Intermediate Zone (IZ) 2001 code (Scotland), return
a list of all the surrounding secondary schools whose probabilty of being visited by the MSOA_IZ is
greater than or equal to the threshold.
School ids are taken from the Edubase list of URN
NOTE: code identical to the primary school version, only with switched lookup tables
@param msoa_iz An MSOA code (England/Wales e.g. E02000001) or an IZ2001 code (Scotland e.g. S02000001)
@param threshold Probability threshold e.g. 0.5 means return all possible retail points with probability>=0.5
@returns a list of [ {id: 'retailid1', p: 0.5}, {id: 'retailid2', p:0.6}, ... etc] (NOTE: not sorted in any particular order)
"""
def getProbableRetailByMSOAIZ(msoa_iz,threshold):
    result = []
    #onsModelBasedIncome2011
    zonei = int(dfRetailPointsPopulation.loc[dfRetailPointsPopulation['msoaiz'] == msoa_iz, 'zonei'])
    m,n = retailpoints_probSij.shape
    for j in range(n):
        p = retailpoints_probSij[zonei,j]
        if p>=threshold:
            row2 = dfRetailPointsZones.loc[dfRetailPointsZones['zonei'] == j] #yes, zonei==j is correct, they're always called 'zonei'
            id = row2['URN'].values[0]
            result.append({'id':id, 'p':p})
        #end if
    #end for
    return result

################################################################################

"""
TODO: hospitals version
"""

################################################################################
