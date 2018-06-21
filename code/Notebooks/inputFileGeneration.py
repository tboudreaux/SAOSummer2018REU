import pandas as pd
import numpy as np
import ipywidgets as iw

def get_input_grid_rows():
    nbody6Row1 = ['KSTART', 'TCOMP', 'TCRITp', 'isernb', 'iserreg', 'iserks']

    inputRow1 = ['N', 'NFIX', 'NCRIT', 'NRAND', 'NNBOPT', 'NRUN']
    inputRow2 = ['ETAI', 'ETAR', 'RSO', 'DTADJ', 'DELTAT', 'TCRIT', 'QE', 'RBAR', 'ZMBAR']
    inputRow3 = ['KZ({a})'.format(a=i) for i in range(1, 11)]
    inputRow4 = ['KZ({a})'.format(a=i) for i in range(11, 21)]
    inputRow5 = ['KZ({a})'.format(a=i) for i in range(21, 31)]
    inputRow6 = ['KZ({a})'.format(a=i) for i in range(31, 41)]
    inputRow7 = ['KZ({a})'.format(a=i) for i in range(41, 51)]
    inputRow8 = ['DTMIN', 'RMIN', 'ETAU', 'ECLOSE', 'GMIN', 'GMAX', 'SMAX']

    dataRow1 = ['ALPHA', 'BODY1', 'BODYN', 'NBINO', 'NHIO', 'ZMET', 'EPOCHO', 'DTPLOT']

    setupRow1 = ['APO', 'ECC', 'N2', 'SCALE']
    setupRow2 = ['APO', 'ECC', 'SCALE']
    setupRow3 = ['APO', 'ECC', 'SCALE']
    setupRow4 = ['SEMI', 'ECC', 'M1', 'M2']
    setupRow5 = ['ZMH', 'RCUT']

    scaleRow1 = ['Q', 'VXROT', 'VZROT', 'RTIDE']

    xtrn10Row1 = ['GMG', 'RGO']
    xtrn10Row2 = ['GMG', 'DISK', 'A', 'B', 'VCIRC', 'RCIRC', 'GMB', 'AR', 'GAM']
    xtrn10Row3 = ['RGx', 'RGy', 'RGz', 'VGx', 'VGy', 'VGz']
    xtrn10Row4 = ['MP', 'AP', 'MPDOT', 'TDELAY']

    binpopRow1 = ['SEMI', 'ECC', 'RATIO', 'RANGE', 'NSKIP', 'IDORM']

    hipopRow1 = ['SEMI', 'ECC', 'RATIO', 'RANGE']

    imbhinitRow1 = ['MMBH', 'XBH(1)', 'XBH(2)', 'XBH(3)', 'VBH(1)', 'VBH(2)', 'VBH(3)', 'DTBH']

    cloud0Row1 = ['NCL', 'RB2', 'VCL', 'SIGMA', 'CLM', 'RCL2']

    Rows = [nbody6Row1, inputRow1, inputRow2, inputRow3, inputRow4, inputRow5, inputRow6,
            inputRow7, inputRow8, dataRow1, setupRow1, setupRow2, setupRow3, setupRow4,
            setupRow5, scaleRow1, xtrn10Row1, xtrn10Row2, xtrn10Row3, xtrn10Row4, binpopRow1,
            hipopRow1, imbhinitRow1, cloud0Row1]
    
    Names = ['nbody6.F', 'input.F', 'data.F', 'setup.F', 'scale.F', 'xtrn10.F',
             'binpop.F', 'hipop.F', 'imbhinit.F', 'cloud0.F']
    
    return Rows, Names

def read_input_grid(path):
    with open(path, 'r') as grid:
        rows = grid.readlines()
    rows = [row.strip('\n').split(' ') for row in rows]
    return rows

def display_grid(Rows, Names, grid=None):
    boxs = list()
    groups = list()
    ccurent = 0
    cuts = [0, 8, 9, 14, 15, 19, 20, 21, 22, 23]

    for i, row in enumerate(Rows):
        if grid:
             attrib = [iw.Text(placeholder=w, value=v) for w, v in zip(row, grid[i])]
        else:
             attrib = [iw.Text(placeholder=w) for w in row]
        row = iw.HBox([a for a in attrib])
        boxs.append(row)


        if i == cuts[ccurent]:
            groups.append(iw.VBox(boxs))
            boxs = list()
            ccurent += 1

    accord = iw.Accordion(children=groups)
    for i, name in enumerate(Names):
        accord.set_title(i, name)

    return accord, groups

def input_grid_generation(Rows, Names, grid=None):
    widget, groups = display_grid(Rows, Names, grid=grid)
    save = iw.Button(description='Save Input File')
    filename = iw.Text(placeholder='File Name', value='FileName.txt')
    def save_func(b):
        KZ5 = groups[1].children[2].children[4].value
        KZ8 = groups[1].children[2].children[7].value
        KZ13 = groups[1].children[3].children[2].value
        KZ14 = groups[1].children[3].children[3].value
        KZ18 = groups[1].children[3].children[7].value
        KZ24 = groups[1].children[4].children[3].value
        cRow = 0
        out = list()
        for j, group in enumerate(groups):
            for i, row in enumerate(group.children):
                ap = True
                row_vals = list()
                for cell in row.children: 
                    if cell.value == '':
                            row_vals.append('@')
                    else:
                        row_vals.append(cell.value)
                if not set(row_vals) == {'@'}:
                    out.append(' '.join(row_vals))
                cRow += 1
        save_name = filename.value
        with open(save_name, 'w') as f:
            f.write('\n'.join(out))
        bash_name = save_name.split('.')[0] + '.sh'
        with open(bash_name, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Simulation"\n')
            f.write(f'nbody6++.hdf5 < {save_name} > .')
        

    save.on_click(save_func)
    meta = iw.HBox([save, filename])
    composit = iw.VBox([widget, meta])
    
    return composit

# [Line Number, KZ(#), Value, cell ref, operation]
# cell ref:
#         0 - just look at current cell
#         1 - and comparision to next cell (&&)
#         2 - or comparison to next cell (||)
#         3 - cell compared to previous cell
# operation:
#         1 - KZ(#) == value
#         2 - KZ(#) < value
#         3 - KZ(#) > value
# row_conditons = np.array([[10, 5, 2, 0, 1], [11, 5, 3, 0, 1], [12, 5, 3, 0, 1],
#                          [13, 5, 4, 0, 1], [14, 5, 6, 1, 1], [14, 24, 0, 3, 2],
#                          [16, 14, 2, 0, 1], [18, 14, 3, 0, 1], [19, 14, 3, 2, 1],
#                          [19, 14, 4, 3, 1], [20, 8, 1, 2, 1], [20, 8, 4, 3, 2],
#                          [21, 8, 0, 1, 2], [21, 18, 1, 3, 2], [22, 24, 1, 0, 1],
#                          [23, 13, 0, 0, 2]])
# condition_indexs = np.where(row_conditons[:, 0] == cRow)[0]
# conditions = np.zeros(shape=(len(condition_indexs), 5))
# for i, ci in enumerate(condition_indexs):
#     conditions[i] = row_conditons[ci]
# if conditions.size != 0:
#     tcond = conditions[0]
#     if tcond[1] == 5:
#         if tcond[4] == 1:
#             assert KZ5 == tcond[2]
#         else:
#             raise NameError
#     if tcond[1] == 8