from pyBody import nbodyRun
from pyBody.snapshot import nbody_snapshot

# import matplotlib.pyplot as plt

# snapshot_path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/oldSimulations/runTests/MultiBinaryTest/Binary0-7/Binary0-7/snap.40_8.h5part"
# snapshot = nbody_snapshot(snapshot_path)
# print(snapshot)

old_run_path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/oldSimulations/runTests/MultiBinaryTest/Binary0-0/Binary0-0/"
new_run_path = "/Users/tboudreaux/SAOSummer2018/simulations/externalSimulations/TestSimulations/compileTest/N3k_K_T1000/"
run = nbodyRun(new_run_path)
NAM1 = run.snapset.follow_ID(567, follow_num=60)
print(NAM1)


