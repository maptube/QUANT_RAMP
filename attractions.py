"""
attractions.py
Compute attractions from data - somehow?
This is the Aj vector
"""

import numpy as np

"""
attractions_msoa_from_retail_ponts
Compute attractions as a vector of msoas based on distance to point in msoa and floorspace.
This computes the Aj vector that we need in the model.
Aj=total floorspace 
@param zonecodes
@param retailPointsGeocodedMSOA list of ['name','east','north','floorspace','msoa']
@returns Aj vector where j is the zone i number
"""
def attractions_msoa_floorspace_from_retail_points(zonecodes,retailPointsGeocodedMSOA):
    N = len(zonecodes.dt)
    Aj = np.zeros(N)

    #total up all the floorspace in each msoa
    floorspace = {}
    for rp in retailPointsGeocodedMSOA:
        msoa = rp['msoa']
        fs = rp['floorspace']
        if msoa in floorspace:
            floorspace[msoa]=floorspace[msoa]+fs #exiting entry
        else:
            floorspace[msoa]=fs #new entry
    #end for

    #OK, that's totalled up the floorspace of the retail points by msoa, now make a zones table Aj

    for areakey in zonecodes.dt:
        zonej = zonecodes.dt[areakey]['zonei']
        Aj[zonej] = floorspace[msoa]
    #end for

    return Aj

################################################################################
