import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('TKAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import AutoMinorLocator


plt.rc('text', usetex=True)
plt.rc('font', family='serif')

PATH = "../intraRunOutput/ExternalPotentialTest2/N1k_R3_K_xtern/cluser_status.csv"

key = 'RDENS'
df = pd.read_csv(PATH, sep=r'\s+', engine='python')
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot(df["{}1".format(key)], df["{}2".format(key)], df["{}3".format(key)], 'o-')
ax.plot([df.iloc[0]["{}1".format(key)]], [df.iloc[0]["{}2".format(key)]], [df.iloc[0]["{}3".format(key)]], 'go')
ax.plot([df.iloc[-1]["{}1".format(key)]], [df.iloc[-1]["{}2".format(key)]], [df.iloc[-1]["{}3".format(key)]], 'ro')

ax.tick_params(axis='both', which='major', labelsize=15, length=12, direction='in')
ax.tick_params(axis='both', which='minor', length=6, direction='in')

ax.view_init(0, 150)

plt.show()