import numpy as np
from math import exp, fabs
from sys import float_info
import time

"""
Single destination constrained gravity model
This is a variant on the Quant model as we have no flows, only Oi and Dj totals.
The TObs flow matrix is fitted to this using beta and constraining so that the
Dj totals are exact.
"""
class SingleDestination:
    #self.NumModes=3 #const???
    
    ###############################################################################

    def __init__(self,m,n):
        print('quantsingledestination ',m,n)
        self.m=m
        self.n=n
        self.OiObs=np.zeros(m)
        self.DjObs=np.zeros(n)
        #self.TObs=[] #Data input to model list of NDArray
        self.cij=[] #cost matrix for zones in TObs

        self.TPred=[] #this is the output
        self.Beta=1.0

    ###############################################################################

    """
    setOi
    Given a data frame containing one column with the zone number (i) and one column
    with the actual data values, fill the Oi origins property with data so that
    the position in the Oi numpy array is the zonei field of the data.
    The code is almost identical to the setDj method.
    NOTE: max(i) < self.m
    """
    def setOi(self,df,zoneiColName,dataColName):
        df2=df.sort_values(by=[zoneiColName])
        self.OiObs = df2[dataColName].to_numpy()
        assert len(self.OiObs)==self.m, "FATAL: setOi length Oi="+str(len(self.OiObs))+" MUST equal model definition size of m="+str(self.m)


    ###############################################################################

    """
    setDj
    Given a data frame containing one column with the zone number (j) and one column
    with the actual data values, fill the Dj destinations property with data so that
    the position in the Dj numpy array is the zonei field of the data.
    The code is almost identical to the setOi method.
    NOTE: max(i) < self.n
    """
    def setDj(self,df,zoneiColName,dataColName):
        df2=df.sort_values(by=[zoneiColName])
        self.DjObs = df2[dataColName].to_numpy()
        assert len(self.DjObs)==self.n, "FATAL: setDj length Dj="+str(len(self.DjObs))+" MUST equal model definition size of n="+str(self.n)


    ###############################################################################


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


    ###############################################################################


    """
    calculateCBar
    Mean trips calculation
    @param name="Tij" NDArray
    @param name="cij" NDArray
    @returns float
    """
    def calculateCBar(self,Tij,cij):
        #(M, N) = np.shape(Tij)
        #CNumerator = 0.0
        #CDenominator = 0.0
        #for i in range(0,N):
        #    for j in range(0,N):
        #        CNumerator += Tij[i, j] * cij[i, j]
        #        CDenominator += Tij[i, j]
        #CBar = CNumerator / CDenominator
        #print("CBar=",CBar)
        #faster
        CNumerator2 = np.sum(Tij*cij)
        CDenominator2 = np.sum(Tij)
        CBar2=CNumerator2/CDenominator2
        print("CBar2=",CBar2)

        return CBar2

    ###############################################################################

    """
    Calculate Oi for a trips matrix.
    Two methods are presented here, one which is simple and very slow and one
    which uses python vector maths and is much faster. Once 2 is proven equal
    to 1, then it can be used exclusively. This function is mainly used for
    testing with the TensorFlow and other implementations.
    """
    def calculateOi(self,Tij):
        (M, N) = np.shape(Tij)
        #OiObs
        Oi = np.zeros(N)
        #Method 1 - slow, but simplest implementation for testing with
        #for i in range(0,N):
        #    sum = 0.0
        #    for j in range(0,N):
        #        sum += Tij[i, j]
        #    Oi[i] = sum
        #Method 2 - MUCH FASTER! But check that it is identical to method 1
        Oi=Tij.sum(axis=1)
        return Oi

    ###############################################################################

    """
    Calculate Dj for a trips matrix.
    Two methods are presented here, one which is simple and very slow and one
    which uses python vector maths and is much faster. Once 2 is proven equal
    to 1, then it can be used exclusively. This function is mainly used for
    testing with the TensorFlow and other implementations.
    """
    def calculateDj(self,Tij):
        (M, N) = np.shape(Tij)
        #DjObs
        Dj = np.zeros(N)
        #Method 1 - slow, but simplest implementation for testing with
        #for j in range(0,N):
        #    sum = 0.0
        #    for i in range(0,N):
        #        sum += Tij[i, j]
        #    Dj[j] = sum
        #Method 2 - MUCH FASTER! But check that it is identical to method 1
        Dj=Tij.sum(axis=0)
        return Dj

    ###############################################################################

    """
    run
    Run the model, in other words, train it.
    NOTE: there are no flows for this model - it works on the Oi and Dj inputs.
    Output is a flow matrix and beta that gets this result using Oi,Dj and costs.
    @returns nothing
    """
    def run(self):
        #(M, N) = np.shape(self.TObs[0])
        
        #set up Beta to be 1.0 then converge down
        beta = 0.13 #from the quant calibration #should start at 1.0

        #work out Dobs and Tobs from rows and columns of TObs matrix
        #These don't ever change so they need to be outside the convergence loop
        #DjObs = np.zeros(N) #np.arange(N)
        #OiObs = np.zeros(N) #np.arange(N)
        #sum=0.0

        #OiObs
        #for i in range(0,N):
        #    sum = 0.0
        #    for j in range(0,N):
        #        for k in range(0, self.numModes):
        #            sum += self.TObs[k][i, j]
        #    OiObs[i] = sum
        #MUCH FASTER!
        #ksum=np.array([np.zeros(N),np.zeros(N),np.zeros(N)])
        #for k in range(0,self.numModes):
        #    ksum[k]=self.TObs[k].sum(axis=1)
        #OiObs = ksum.sum(axis=0)
        #print("check 1: ",OiObs[0],ksum[0][0]+ksum[1][0]+ksum[2][0])
        #print("check 1: ",OiObs2[0])
        #for i in range(0,N):
        #    print(OiObs[i],OiObs2[i])

        #DjObs
        #for j in range(0,N):
        #    sum = 0.0
        #    for i in range(0,N):
        #        for k in range(0,self.numModes):
        #            sum += self.TObs[k][i, j]
        #    DjObs[j] = sum
        #MUCH FASTER!
        #ksum=np.array([np.zeros(N),np.zeros(N),np.zeros(N)])
        #for k in range(0,self.numModes):
        #    ksum[k]=self.TObs[k].sum(axis=0)
        #DjObs = ksum.sum(axis=0)
        #for i in range(0,N):
        #    print(DjObs[i],DjObs2[i])

        #print("OiObs and DjObs calculated")


        Tij = np.zeros(self.m*self.n,dtype=float).reshape(self.m, self.n) #array of flow matrix - need declaration outside loop

        converged=False

        while not converged:
            #model run
            #Tij = [np.zeros(N*N).reshape(N, N) for k in range(0,self.numModes) ]
            #pre-calculate exp(-Beta[k]*self.Cij[k]) for speed
            expBetaCij = np.exp(-beta*self.cij)

            for j in range(0,self.n):
                #denominator calculation which is sum of all modes
                #denom = 0.0  #double
                #for kk in range(0,self.numModes): #second mode loop
                #    for i in range(0,N):
                #        denom += OiObs[i] * exp(-Beta[kk] * self.Cij[kk][i, j])
                #    #end for j
                ##end for kk
                #print("denom=",denom)
                #faster...?
                denom2=np.sum(self.OiObs*expBetaCij[:,j])
                #print(denom2)

                #numerator calculation for this mode (k)
                #for i in range(0,N):
                #    Tij[k][i, j] = B[j] * OiObs[i] * DjObs[j] * exp(-Beta[k] * self.Cij[k][i, j]) / denom
                #print("Tijk[0,0]=",Tij[k][i,0])
                #faster
                Tij2=self.DjObs[j]*(self.OiObs*expBetaCij[:,j]/denom2)
                Tij[:,j]=Tij2 #put answer slice back in return array 
                #print("Tijk2[0,0]=",Tijk2[0])
            #end for i

            #we have no TijObs, so no CBarObs to use as an error metric - going to have to use Dj sums instead
            OiPred = self.calculateOi(Tij)
            OiPredSum = np.sum(OiPred)
            OiObsSum = np.sum(self.OiObs)
            DjPred = self.calculateDj(Tij)
            DjPredSum = np.sum(DjPred)
            DjObsSum = np.sum(self.DjObs)
            delta = OiPredSum-OiObsSum

            #delta check on beta stopping condition for convergence
            #gradient descent search on beta
            converged = True
            #if delta / OiObsSum > 0.001:
            #    beta = beta * OiPredSum / OiObsSum
            #    converged = False
            print("beta=",beta,"delta=",delta,"OiPredSum",OiPredSum,"OiObsSum",OiObsSum,"DjPredSum",DjPredSum,"DjObsSum",DjObsSum)
        #end while not Converged

        CBarPred = self.calculateCBar(Tij,self.cij)
        print("CBarPred = ",CBarPred)

        #Set the output, TPred[] and beta that gives us the best answer
        self.TPred = Tij
        self.Beta = beta

    ###############################################################################

    """
    Added to allow timing of the main loop for speed comparison with the TensorFlow code.
    NOTE: this is only single mode and one iteration of the main loop. This is what all the benchmark tests do.
    """
    def benchmarkRun(self,numRuns,Tij,Cij,Beta):
        #run Tij = Ai * Oi * Dj * exp(-Beta * Cij)   where Ai = 1/sumj Dj*exp(-Beta * Cij)
        (M, N) = np.shape(Tij)
        starttime = time.time()
        for r in range(0,numRuns):
            TPred = np.zeros(N*N).reshape(N, N)
            Oi = self.calculateOi(Tij)
            Dj = self.calculateDj(Tij)
            expBetaCij = np.exp(-Beta*Cij) #pre-calculate an exp(-Beta*cij) matrix for speed
            for i in range(0,N):
                denom = np.sum(Dj*expBetaCij[i,:]) #sigmaj Dj exp(-Beta*Cij)
                Tij2=Oi[i]*(Dj*expBetaCij[i]/denom)
                TPred[i,:]=Tij2 #put answer slice back in return array
            #end for i
        #end for r
        finishtime = time.time()
        #print("SingleDest: benchmarkRun ",finishtime-starttime," seconds")
        return (TPred,finishtime-starttime)

    ###############################################################################
