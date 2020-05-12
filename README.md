# QUANT_RAMP
RAMP using QUANT accessibilities

Retail model using data from Geolytix and the 2011 Census

NOTE:
This is still very much a work in progress and currently lacks the installation parts to allow it to be run stand alone.
There are comments in the code as to where the base data needs to come from, but it's not going to be easy to make
it work yet.

# INSTALLATION
File structure:

|
+ QUANTRampAPI.py
|
+ model-runs
  |
  + zonecodes.csv
  + primaryProbPij.bin
  + primaryZones.csv
  + primaryAttractors.csv
  + secondaryPij.bin
  + secondaryZones.csv
  + secondaryAttractors.csv
 
(so that's the QUANTRampAPI.py file containing the interface with a model-runs dir containing all the data - file constants are defined in the Python file)
 
Full documentation is in the Python file, but you basically specify an MSOA or IZ code and a threshold and it retuns a list of probabilities and school location IDs which match the primaryZones file.
