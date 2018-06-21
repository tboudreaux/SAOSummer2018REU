
# Written based on Mac OS 10.13.2
# Last Updated: June 8th 2018
# Detailed manual in docs directory of nbody6++gpu source code
# git hub page: https://github.com/nbodyx/Nbody6ppGPU.git
# Based on python version 3.6.2

Installation:
    $ git clone https://github.com/nbodyx/Nbody6ppGPU.git
    $ cd Nbody6ppGPU
    $ vim src/Main/intgrt.F
    - Go to line 561 and delete the ampersand, and the new line character
    -   making line the original content of line 561 move to the end
    -   of line 560. Then insert a new line break and a new ampersand
    -   thus making the file look as it did originally. We do this because
    -   there is a non ASCII whitespace character in that file (likely a
    -   windows line break) that the fortran compiler will fail at, so 
    -   it needs to be removed.
    $ cd ../..
    $ ./configure --enable-hdf5 # And other options if they are pertinent
    $ make
    $ make install
    - If one wants to uninstall nbody6++ simply:
        $ make uninstall

Programs installed when running the following auto config setup:
    $ ./configure --disable-gpu --disable-mpi --enable-simd=avx --disable-openmp --enable-hdf5 --enable-tools
    $ make
    $ make install

    - nb6++dumpb2a  : Currently Unknown
    - nb6++snapshot : Currently Unknown
    - nbody6++.hdf5 : Main program to run simulations

Usage:
    - Assuming one compiled nBody6++ with hdf5 support it will have installed
    -   as nbody6++.hdf5 Check that this is the case
        $ which nbody6++.hdf5
    - If it installed properly then you can use it!

Information about usage:
    Nbody6++ outputs data and diagnostics during its run and data at 
    the end of the run. It take an input file formate as a grid of 
    numbers. Input files and diagnostic file write out is handled through
    standard IO redirection. Run data is written to the current directory.

    One would start an nbody6++ run as follows:

        $ nbody6++.hdf5 < ~/inputFiles/N2_B500_T30.input > ~/diagnosisOutput/2RunOne/diagnosis.dat &

    The file N2k_B500_T30.input contains the following:

        1 1000000.0 1.E6 40 40 40
        2000 1 10 452 100 1 10
        0.02 0.02 0.3 1.0 1.0 1000.0 2.0E-03 1.0 0.7
        0 1 1 0 1 0 4 3 0 2
        0 1 0 0 2 0 0 3 3 6
        1 0 2 0 0 2 0 0 0 2
        1 0 2 0 1 0 1 1 0 0
        0 0 0 0 0 2 1 0 0 0
        1.0E-04 1E-3 0.1 1.0 1.0E-06 0.01 0.25
        2.35 100.0 0.08 500 30 0.001 0 1.0
        0.5 0.0 0.0 0.0
        2.E-4 -1.0 1.0 1.E3 5 0
        1.E-5 -1.0 1.0 5.0 0

    This file contains a lot of information. To fully understand it go to page 10-19 in the nbody6++GPU manual. The most important things to note quickly are that all floating point numbers must be written with a decimal, and all integers must be written as integers (i.e. don't write 1.0 where it calls for an integer or 1 where it calls for a floating point value)

    I will leave most of the options up to the reader to find (they are all listed out nicely in those pages specified above); however, KZ(46) and KZ(47) (the 2 and 1 on the 6th row up from the bottom) are important. KZ(46) (the 2) controls what format snapshots write out as. Setting this to 2 or 4 writes them (the snapshots) out in the hdf5 file format. The different between 2 and 4 is that 2 only writes out ``active stars'' every time step while 4 outputs the full particle list every time step. 1 and 3 have the same distinction between them as 2 and 4; however, they write snapshots as ASCII files instead of hdf5 files. All this information, and other important information can be found in the manual. 

    If you run the code using one of the included samples (in the samples directory) as the input you will get a large number of files in the directory where you ran the command to start nbody6++. Most of these files are ASCII files (even if you have compiled with, and have set hdf5 write out on). A list of what different files are can be found in pages 38-57 of the manual. Below I highlight some of the most important ones:

        global.# -> file which contains a lot of information (listed on page 47 of the manual) about the dynamics of the cluster as a whole. [ASCII]

        status.# -> file which contains a lot of information (listed on page 47 of the manual) about the mass and energy of the cluster [ASCII]

        snapshot.#_#.h5part -> snapshot information, each files is one time--step, denoted by the second number in the files name (time the file was written in NBody Units -- Page 37). [hdf5]

    There are many other files that are important; for more information on those see the back of the manual. 

Reading Snapshots:
    Snapshots are stored in the hdf5 data format. To read these files in python it is recommended you use h5py. This can be installed with pip:

        $ pip install h5py

    Once h5py is installed each h5part snapshot file can be opened independently (remember that the file name for each snapshot indicates its associated time). each file is broken down as follows

                                            snapshot.#_#.h5part
                                                      |
                                                      |
                                                      |
                                                    Snap#n
                                                      |- Binaries 
                                                      |- Mergers          
                                                      |- KW 
                                                      |- MC 
                                                      |- M  
                                                      |- NAM
                                                      |- POT                    
                                                      |- RC
                                                      |- RS
                                                      |- TE
                                                      |- V1
                                                      |- V2
                                                      |- V3
                                                      |- X1
                                                      |- X2
                                                      |- X3
    The Binaries, Mergers, and KW fields all have there own subfields (of a similar form to these but for multiple objects in each row). Here I will focus on the fields excluding Binaries, Mergers, and KW. They can be accessed as follows (python code)

        import h5py
        f = h5py.File('filepath/filename.h5part', 'r')

        X1 = f['Step#0']['X1']
        X2 = f['Step#0']['X2']

    And so on. If one wanted to access data inside say Binaries or Mergers one might call that information by

        import h5py
        f = h5py.File('filepath/filename.h5part', 'r')

        data = f['Step#0']['Binaries'/'Mergers'][keyname]

    keys for Binaries / Mergers  are listed below

        Binaries:                               Mergers:
            A        POT      XR1                   A0      NAM1    VR03
            ECC      RC1      XR2                   A1      NAM2    VR11
            G        RC2      XR3                   ECC0    NAMC    VR12
            KW1      RS1                            ECC1    P       VR13
            KW2      RS2                            KW1     POT     XC1
            KWC      TE1                            KW2     RC1     XC2
            L1       TE2                            KW3     RC2     XC3
            L2       VC1                            KWC     RS1     XR01
            M1       VC2                            L1      RS2     XR02
            M2       VC3                            L2      TE1     XR03
            MC1      VR1                            L3      TE2     XR11
            MC2      VR2                            M1      VC1     XR12
            NAM1     VR3                            M2      VC2     XR13
            NAM2     XC1                            M3      VC3
            NAMC     XC2                            MC1     VR01
            P        XC3                            MC2     VR02

    Detailed breakdowns of what these keys represent can be found in the manual split between pages 52-53, and pages 38-42.

Basic Python 3D Visualizations of data:
    All 2D data can be easily visualize using matplotlib or other plotting libraries in python, and as such will not be extensively touched upon here (recall that this information is stored in files such as global.# and status.#, for more information see Basic Python 2D Visualization of data Section). However, 3D can be more challenging to represent, especially when one wants to interactively explore the 3D data. One nice way of doing this is through a combination of jupyter lab (the latest iteration of the widely used jupyter notebook), ipywidgets, and ipyvolume. Start by installing jupyter lab

        $ pip install jupyterlab

    Now restart your shell. Then we need to install the module that will allow for 3D visualization --- ipyvolume.

        $ pip install ipympl
        $ pip install ipywidgets
        $ pip install ipyvolume
        $ pip install ipyvolumejupyter labextension install @jupyter-widgets/jupyterlab-manager
        $ jupyter labextension install ipyvolume

    If you run into errors during installation, or in the following steps refer to the following threads for guidance: https://github.com/maartenbreddels/ipyvolume/issues/127 & https://github.com/maartenbreddels/ipyvolume/issues/102

    Launch jupyter lab 

        $ jupyter lab

    make a new notebook which will be used to demonstrate basic 3D visualization of data. The following code should build a quiver plot showing the ``active stars'' in the cluster at any given time--step (NB: this code *must* be run in a jupyter notebook to work properly. Additionally, the max parameter specified in the interact function call may change depending on the simulation specifics.).

        import numpy as np
        import h5py
        import ipyvolume as ipv
        from ipywidgets import IntSlider, interact
        import matplotlib.cm

        def plot_cluster(part, step):
            path = f'[FILEPATH]/snap.40_{part}.h5part'
            f = h5py.File(path, 'r')

            X1 = f[f'Step#{step}']['X1']
            X2 = f[f'Step#{step}']['X2']
            X3 = f[f'Step#{step}']['X3']

            V1 = f[f'Step#{step}']['V1']
            V2 = f[f'Step#{step}']['V2']
            V3 = f[f'Step#{step}']['V3']

            R = f[f'Step#{step}']['RS']
            L = f[f'Step#{step}']['L']
            V = np.sqrt(np.power(list(V1), 2)+np.power(list(V2), 2)+np.power(list(V3), 2))

            color_var = V
            ipv.figure()
            colormap = matplotlib.cm.viridis
            c = colormap(np.linspace(min(color_var), max(color_var), len(color_var)))
            ipv.quiver(X1, X2, X3, V1, V2, V3, size=R, color=c)

            # ipv.scatter(X1, X2, X3, size=R, marker='sphere', color=c)
            ipv.show()

        interact(plot_cluster, part=IntSlider(min=0, max=50, step=1, value=0), part=IntSlider(min=0, max=3, step=1, value=0))

    This should produce a drag-able, zoomable plot in jupyter lab with two sliders. One slider will allow the plot to be pulled through time (part) and the other will change the step that the plot is displaying (Step#0 vs. Step#1/2/3)

    Aside from Python, the open source program paraview can be used to visualize the 3D data stored in the snapshots. Simply download and install paraview, click on the button to open a new file, navigate to the directory where snapshots are stored. Paraview may have collapsed all the h5part files into a single file or not, if it has click on the one file, if not select a single snapshot and open. Now in the bottom left of the screen change the X Y and Z variables to be the desired X Y and Z variables, and if you want set the color map variable in the check box below. Then click apply and the data should be shown in the viewfinder.

Basic Python 2D Visualization of Data:
    Focusing for the moment on the status.# file. This file will only be written out if KZ(46) > 0. This file can be read in with the python module pandas

        import pandas as pd
        import matplotlib.pyplot as plt

        df = pd.read_csv('[FILEPATH]/status.#', sep=r'\s*')

        time = df.iloc[:, 1]
        Rtid = df.iloc[:, 9]
        Mmass = df.iloc[:, 15]

        plt.plot(time, Rtid, 'o--')
        plt.xlabel('Time [Myr]')
        plt.ylabel('Tidal Radius [pc]')

        plt.show()

        plt.plot(time, Mmas, 'o--')
        plt.xlabel('Time [Myr]')
        plt.ylabel(r'Maximum Particle Mass [M$_{\odot}$]')

        plt.show()

    Note that I use the delimiter r'\s*' as it is the regular expression representing general whitespace. To figure out which column contains which information, reference the manual on page 49.

Extermal Files:
    In lew of the included mass distributions externally generated mass distributions can be read in. To do this make sure KZ(5) = 0. Then KZ(22) will be the pertinant option. Then if KZ(22) >= 2 data will be read externally. The format of this data is dependant on the exact setting of KZ(22). As an example in the nbody format

