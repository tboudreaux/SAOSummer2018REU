import h5py
import numpy as np
import pandas as pd
import os
import re


def __tryint__(s):
    try:
        return int(s)
    except:
        return s
     
def __alphanum_key__(s):
    return [ __tryint__(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    l.sort(key=__alphanum_key__)
    return l

class nbody_snapshot:
    def __init__(self, path):
        self.file = self.__read_snapshot__(path)
        self.TTOT = int(path.split('/')[-1].split('_')[1].split('.')[0])
        self.steps = len(self.file)
        self.current_step = 0
        self.single_star_data = self.__get_single_star_data__()
        self.center = (self.single_star_data.X1.mean(),
                       self.single_star_data.X2.mean(),
                       self.single_star_data.X3.mean())
    
    @staticmethod
    def __read_snapshot__(path):
        f = h5py.File(path)
        return f
    
    def __get_single_star_data__(self):
        rd = self.file[f'Step#{self.current_step}']
        keys_i = ['NAM', 'X1', 'X2', 'X3', 'V1', 'V2', 'V3', 'M', 'L', 'MC', 'RC', 'RS', 'POT', 'TE']
        de = dict()
        for key in keys_i:
            de[key] = rd[key]
        df = pd.DataFrame(data=de)
        # df = df.set_index('NAM')
        return df
    
    def __get_binaries_data__(self):
        rd = self.file[f'Step#{self.current_step}']
        keys_i = ['NAM', 'X1', 'X2', 'X3', 'V1', 'V2', 'V3', 'M', 'L', 'MC', 'RC', 'RS', 'POT', 'TE']
        de = dict()
        for key in keys_i:
            de[key] = rd[key]
        df = pd.DataFrame(data=de)
        df = df.set_index('NAM')
        return df
    
    def save_single_star_data(self, filename, sep=','):
        self.single_star_data.to_csv(filename, sep=sep, index=False)
        
    def __repr__(self):
        out = list()
        out.append(f'|---------------------------')
        out.append(f"| Snapshot     | {self.TTOT}")
        out.append(f"| N            | {len(self.single_star_data)}")
        out.append(f"| Centered at  | {self.center}")
        out.append(f'|---------------------------')
        return '\n'.join(out)

class snapshot_set:
    def __init__(self, basepath):
        h5files = [x for x in os.listdir(basepath) if '.h5part' in x]
        h5files = __sort_nicely__(h5files)
        self.snapshots = [nbody_snapshot(f"{basepath}/{x}") for x in h5files]
        
    def follow_ID(self, ID):
        times = list()
        df = self.snapshots[0].single_star_data[self.snapshots[0].single_star_data['NAM'] == ID]
        times.append(self.snapshots[0].TTOT)
        for snapshot in self.snapshots[1:]:
            if len(snapshot.single_star_data[snapshot.single_star_data['NAM'] == ID]) != 0:
                tdf = snapshot.single_star_data[snapshot.single_star_data['NAM'] == ID]
                times.append(snapshot.TTOT)
                df = df.append(tdf)
        df['Time'] = times
        return df.reset_index(drop=True)
    
    def dump_set(self, path, name, sep=','):
        if path[-1] == '/':
            path = path[:-1]
        if not os.path.exists(path):
            os.mkdir(path)
        filenames = [f"{path}/{name}_{snap.TTOT}.csv" for snap in self.snapshots]
        for snap, filename in zip(self.snapshots, filenames):
            snap.save_single_star_data(filename, sep=sep)
