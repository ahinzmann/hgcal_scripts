# Setup CMSSW simulation:

source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_15_1_0_pre5
cd CMSSW_15_1_0_pre5/src/
cmsenv
scram b -j 10

git cms-addpkg Geometry/HGCalTBCommonData
git cms-addpkg SimG4CMS/HGCalTestBeam
git cms-addpkg IOMC/ParticleGuns
git cms-addpkg Fireworks/Core
git cms-addpkg Fireworks/Geometry
git cms-addpkg Fireworks/Calo
git remote add ahinzmann git@github.com:ahinzmann/cmssw.git
git fetch ahinzmann teststand
git checkout teststand
scram b -j5

# Run simulation

cmsRun Geometry/HGCalTBCommonData/test/python/testHGCalTB24DESYV2_teststand_cfg.py

# Run simulation on condor

condor_submit condor.submit

# Make plots

python teststand_sim_plots.py

