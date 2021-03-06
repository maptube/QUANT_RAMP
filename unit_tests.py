################################################################################
# unit_tests.py                                                                #
# Unit tests for the QUANT RAMP API functions                                  #
#                                                                              #
# run with py unit_tests.py                                                    #
################################################################################

from QUANTRampAPI import getProbablePrimarySchoolsByMSOAIZ, getProbableSecondarySchoolsByMSOAIZ
from QUANTRampAPI import getProbableRetailByMSOAIZ
from QUANTRampAPI import getProbableHospitalByMSOAIZ

"""
Test of retrieving data from the API for primary school probability.
Of course, the actual data returned changes depending on what's in the
tables, so it's really only a test of functionality and not that the
numeric result is correct.
"""
def testPrimarySchools():
    print("testPrimarySchools:: running test 1, prob =0.002")
    schools = getProbablePrimarySchoolsByMSOAIZ('E02000001',0.002)
    print(schools)
    print("testPrimarySchools:: running test 2, prob =0.002")
    schools = getProbablePrimarySchoolsByMSOAIZ('E02002559',0.002)
    print(schools)
    print("testPrimarySchools:: running test 3, prob =0.002")
    schools = getProbablePrimarySchoolsByMSOAIZ('S02000530',0.002)
    print(schools)



################################################################################

def testSecondarySchools():
    print("testSecondarySchools:: running test 1, prob =0.002")
    schools = getProbableSecondarySchoolsByMSOAIZ('E02000001',0.002)
    print(schools)
    print("testSecondarySchools:: running test 2, prob =0.002")
    schools = getProbableSecondarySchoolsByMSOAIZ('E02002559',0.002)
    print(schools)
    print("testSecondarySchools:: running test 3, prob =0.002")
    schools = getProbableSecondarySchoolsByMSOAIZ('S02000530',0.002)
    print(schools)

################################################################################
def testRetailPoints():
    print("testRetailPoints:: running test 1, prob =0.002")
    retailpoints = getProbableRetailByMSOAIZ('E02000001',0.002)
    print(retailpoints)

################################################################################

def testHospitalPoints():
    print("testHospitalPoints:: running test 1, prob =0.002")
    hospitalpoints = getProbableHospitalByMSOAIZ('E02000001',0.002)
    print(hospitalpoints)


################################################################################
# MAIN PROGRAM                                                                 #
################################################################################

#testPrimarySchools()
#testSecondarySchools()
#testRetailPoints()
testHospitalPoints()
