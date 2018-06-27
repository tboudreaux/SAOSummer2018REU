import pandas as pd
import numpy as np
import re
import os

from ..utils import sort
from ..utils import misc

class sev_base:
    def __init__(self, path, load=True):
        self.NBtime = path.split('/')[-1].split('_')[1]
        self.path = path
        self.loaded = False
        if load: 
            self.load()

    @staticmethod
    def load_time(path):
        with open(path, 'r') as f:
            time = f.readline()
        time = time.split()[1]
        return time


    def load(self):
        self.time = self.load_time(self.path)
        names=['Time', 'I', "NAME", "K*", "RI", "M", "L", "RS", "Teff"]
        self.df = pd.read_csv(self.path, sep=r'\s+', engine='python', skiprows=1, names=names)
        self.loaded = True

    def deload(self):
        del(self.df)
        del(self.time)
        self.loaded = False

    def __getitem__(self, key):
        assert self.loaded

        if isinstance(key, str):
            if key[:4] == "NAM:":
                key = int(key[4:])
                result = self.df[self.df["NAME"] == key]
            else:
                raise KeyError(f"Unknown spesifier: {key[:4]}")
        else:
            result = self.df.iloc[key]

        return result

    def __repr__(self):
        out = list()
        out.append(f'|---------------------------')
        out.append(f'| Time [NB]    : {self.NBtime}')
        out.append(f'| Loaded       : {self.loaded}')
        if self.loaded:
            out.append(f'| Time [Myr]   : {self.time}')
            out.append(f'| Length       : {len(self.df)}')
        out.append(f'|---------------------------')
        return '\n'.join(out)


class sev_reader:
    def __init__(self, path, buffer_size=50, buffer_shift=3):
        self.buffer_size = buffer_size
        self.buffer_shift = buffer_shift
        self.buffer_init = 0
        self.path = (path[:-1] if path[-1] == '/' else path)
        self.sev_files = sort.sort_nicely([x for x in os.listdir(path) if 'sev.83_' in x])
        self.num_sevs = len(self.sev_files)
        self.sevs, self.loaded = self.__build_buffer__(self.sev_files, self.path,
                                                       self.buffer_init, self.buffer_size)

    @staticmethod
    def __build_buffer__(files, basepath, init, buffer_size):
        to_load = misc.load_list(len(files), init, buffer_size)
        return [sev_base(f"{basepath}/{x}", load) for x, load in zip(files, to_load)], to_load
    
    def __clear_buffer__(self):
        for sev, load in zip(self.sevs, self.loaded):
            if load:
                sev.deload()

    def __shift_buffer__(self, init):
        self.buffer_init = init
        to_load = misc.load_list(self.num_sevs, init, self.buffer_size)
        for sev, new_load, old_load in zip(self.sevs, to_load, self.loaded):
            if old_load and not new_load:
                sev.deload()
            if new_load and not old_load:
                sev.load()
        self.loaded = to_load

    def __reset_buffer__(self, init, hard_reset=False,):
        if hard_reset:
            self.__clear_buffer__()
            self.sevs, self.loaded = self.__build_buffer__(self.sev_files,
                                                           self.path, init,
                                                           self.buffer_size)
        else:
            self.__shift_buffer__(init)

    def __build_tn_buffer__(self, n):
        """
        Build the temporary numeric buffer
        """
        if not self.loaded[n]:
            self.sevs[n].load()

    def __clear_tn_buffer__(self, n):
        if not self.loaded[n]:
            self.sevs[n].deload()

    def __access_tn_buffer__(self, n, query):
        self.__build_tn_buffer__(n)
        query_results = query(self.sevs[n])
        self.__clear_tn_buffer__(n)
        return query_results

    def get_sev(self, n=0):
        if not self.loaded[n]:
            self.__shift_buffer__(n)
        return self.sevs[n]

    def xget_sev(self, start=0, stop=None):
        if not stop:
            stop = self.num_sevs
        if not set(self.loaded[start:start+self.buffer_size]) == {True}:
            self.__reset_buffer__(start)
        for i in range(start, stop):
            yield self.get_sev(n=i)

    def follow_ID(self, ID, start=0, stop=None):
        sev_init = self.get_sev(n=start)
        df = sev_init[f"NAM:{ID}"]
        for sev in self.xget_sev(start=start+1, stop=stop):
            tdf = sev[f"NAM:{ID}"]
            df = df.append(tdf)
        return df.reset_index(drop=True)

    def __repr__(self):
        out = list()
        out.append(f'|---------------------------')
        out.append(f'| Buffer Size  : {self.buffer_size}')
        out.append(f'| Buffer Shift : {self.buffer_shift}')
        out.append(f'| Buffer Init  : {self.buffer_init}')
        out.append(f'| Sev Number   : {self.num_sevs}')
        out.append(f'|---------------------------')
        return '\n'.join(out)

