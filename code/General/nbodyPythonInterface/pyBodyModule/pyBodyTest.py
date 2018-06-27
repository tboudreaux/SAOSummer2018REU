from pyBody import nbodyRun
from pyBody.snapshot import nbody_snapshot
from pyBody.sev import sev_reader, sev_base
from pyBody.lagr import lagr_base

# import matplotlib.pyplot as plt

## Test nbody_snapshot
# snapshot_path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/oldSimulations/runTests/MultiBinaryTest/Binary0-7/Binary0-7/snap.40_8.h5part"
# snapshot = nbody_snapshot(snapshot_path)
# print(snapshot)

## Test nrun
# old_run_path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/oldSimulations/runTests/MultiBinaryTest/Binary0-0/Binary0-0/"
# new_run_path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/TestSimulations/compileTest/N3k_K_T1000/"
# run = nbodyRun(new_run_path)
# print(run)
# NAM1 = run.snapset.follow_ID(567, follow_num=60)
# print(NAM1)

## Test sev_base
# path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/TestSimulations/compileTest/N3k_K_T1000/sev.83_0"
# sev = sev_base(path)
# print(sev["NAM:4"])


## Test sev_reader
# path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/TestSimulations/compileTest/N3k_K_T1000/"
# sev = sev_reader(path)
# df = sev.follow_ID(10, stop=50)
# print(df)

## Test lagr_base
path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/TestSimulations/compileTest/N3k_K_T1000/lagr.7"
lagr = lagr_base(path)
print(lagr['V_x'].columns)


