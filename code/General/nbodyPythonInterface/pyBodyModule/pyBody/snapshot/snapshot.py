import h5py
import pandas as pd
from tqdm import tqdm

import os

from ..utils import sort
from ..utils import misc

class nbody_snapshot:
    def __init__(self, path, load=True):
        self.path = path
        self.__init_sequence__(load, reset=True)

    def __init_sequence__(self, load, reset=False):
        if reset:
            self.TTOT = int(self.path.split('/')[-1].split('_')[1].split('.')[0])
            self.current_step = 0
        if load:
            self.file = self.__read_snapshot__(self.path)
            self.loaded = True
            self.single_star_data, self.time = self.__get_single_star_data__()
            self.steps = len(self.file)
            self.center = (self.single_star_data.X1.mean(),
                           self.single_star_data.X2.mean(),
                           self.single_star_data.X3.mean())


    def __dnit_sequence__(self, reset=False):
        if self.loaded:
            self.file.close()
            del(self.file)
            del(self.single_star_data)
            del(self.time)
            del(self.steps)
            del(self.center)
        if reset:
            self.__init_sequence__(False, reset=True)

    
    @staticmethod
    def __read_snapshot__(path):
        f = h5py.File(path)
        return f

    def load(self, reset=False):
        self.__init_sequence__(True, reset=reset)

    def deload(self, reset=False):
        self.__dnit_sequence__(reset=reset)
    
    def __get_single_star_data__(self):
        assert self.loaded is True

        rd = self.file[f'Step#{self.current_step}']
        time = list(rd.attrs.values())[0]
        keys_i = ['NAM', 'X1', 'X2', 'X3', 'V1', 'V2', 'V3', 'M', 'L', 'MC', 'RC', 'RS', 'POT', 'TE']
        de = dict()
        for key in keys_i:
            de[key] = rd[key]
        df = pd.DataFrame(data=de)
        return df, time
    
    def reload_at_step(self, step):
        assert self.loaded is True
        if step >= len(self.file):
            raise KeyError(f'file does not have Step#{step}')
        self.current_step = step
        self.single_star_data, self.time = self.__get_single_star_data__()

    def save_single_star_data(self, filename, sep=','):
        self.single_star_data.to_csv(filename, sep=sep, index=False)
        
    def xget_steps(self, start=0, stop=None):
        if not stop:
            stop = len(self.file)
        for step in range(start, stop):
            self.reload_at_step(step)
            yield self.single_star_data, self.time

    def __get__(self, key):
        return self.single_star_data[key]

    def __len__(self):
        return len(self.single_star_data)
        
    def __repr__(self):
        out = list()
        last_step = (sort.sort_nicely(list(self.file)))[-1]
        out.append(f'|---------------------------')
        out.append(f"| Snapshot     | {self.TTOT}")
        out.append(f"| N            | {len(self.single_star_data)}")
        out.append(f"| Centered at  | {self.center}")
        out.append(f"| Stat Time    | {list(self.file['Step#0'].attrs.values())[0]}")
        out.append(f"| Stop Time    | {list(self.file[last_step].attrs.values())[0]}")
        out.append(f"| Subsnaps     | {len(self.file)}")
        out.append(f'|---------------------------')
        return '\n'.join(out)


class snapshot_set:
    def __init__(self, basepath, subsnap=False, front_load=True, load_buffer=10,
                 buffer_shift=3):

        if not (load_buffer > buffer_shift + 1):
            raise ValueError('load_buffer must be greater than buffer_shift+1')

        self.buffer_init = 0
        self.buffer = load_buffer
        self.buffer_shift = buffer_shift
        self.basepath = basepath
        h5files = [x for x in os.listdir(basepath) if '.h5part' in x]
        self.h5files = sort.sort_nicely(h5files)
        self.num_snaps = len(self.h5files)
        self.snapshots, self.loaded = self.__build_buffer__(self.h5files, self.basepath,
                                                            self.buffer_init, self.buffer)
        self.subsnap = subsnap


    @staticmethod
    def __build_buffer__(files, basepath, init, buffer_size):
        to_load = misc.load_list(len(files), init, buffer_size)
        return [nbody_snapshot(f"{basepath}/{x}", load=load) for x, load in zip(files, to_load)], to_load
    
    def __clear_buffer__(self):
        for snap, load in zip(self.snapshots, self.loaded):
            if load:
                snap.deload()

    def __shift_buffer__(self, init):
        self.buffer_init = init
        to_load = misc.load_list(self.num_snaps, init, self.buffer)
        for snap, new_load, old_load in zip(self.snapshots, to_load, self.loaded):
            if old_load and not new_load:
                snap.deload()
            if new_load and not old_load:
                snap.load()
        self.loaded = to_load

    def __reset_buffer__(self, hard_reset=False):
        if hard_reset:
            self.__clear_buffer__()
            self.snapshots, self.loaded = self.__build_buffer__(self.h5files,
                                                                self.basepath, 0,
                                                                self.buffer_size)
        else:
            self.__shift_buffer__(0)

    def __build_tn_buffer__(self, n):
        """
        Build the temporary numeric buffer
        """
        if not self.loaded[n]:
            self.snapshots[n].load()

    def __clear_tn_buffer__(self, n):
        if not self.loaded[n]:
            self.snapshots[n].deload()

    def __access_tn_buffer__(self, n, query):
        self.__build_tn_buffer__(n)
        query_results = query(self.snapshots[n])
        self.__clear_tn_buffer__(n)
        return query_results

    def follow_ID(self, ID, start=0, follow_num=None):
        if not set(self.loaded[:self.buffer]) == {True}:
            self.__reset_buffer__()
        times = list()
        df = self.snapshots[start].single_star_data[self.snapshots[start].single_star_data['NAM'] == ID]
        if len(df) != 0:
            times.append(self.snapshots[start].TTOT)
        it = self.snapshots[(start if self.subsnap else start+1):]
        if not follow_num:
            follow_num = self.num_snaps - start
        total=start + follow_num
        for j, snapshot in tqdm(enumerate(it[start:follow_num]), total=total):
            i = start+j
            if i >= (self.buffer_init + self.buffer) - self.buffer_shift:
                self.__shift_buffer__(i)
            if not self.subsnap:
                if len(snapshot.single_star_data[snapshot.single_star_data['NAM'] == ID]) != 0:
                    tdf = snapshot.single_star_data[snapshot.single_star_data['NAM'] == ID]
                    times.append(snapshot.time)
                    df = df.append(tdf)
            else:
                for data, time in snapshot.xget_steps(start=(1 if i == 0 else 0)):
                    tdf = data[data['NAM'] == ID]
                    if len(tdf) != 0:
                        times.append(time)
                        df = df.append(tdf)

        df['Time'] = times
        return df.reset_index(drop=True)
    
    def dump_set(self, path, name, sep=','):
        if path[-1] == '/':
            path = path[:-1]
        if not os.path.exists(path):
            os.mkdir(path)
        filenames = [f"{path}/{name}_{snap.TTOT}.csv" for snap in self.snapshots]
        for i, (snap, filename) in enumerate(zip(self.snapshots, filenames)):
            if i >= (self.buffer_init + self.buffer) - self.buffer_shift:
                self.__shift_buffer__(i)
            snap.save_single_star_data(filename, sep=sep)


    def __repr__(self):
        out = list()
        out.append(f'|---------------------------')
        out.append(f'| Snapshots    : {len(self.h5files)}')
        out.append(f'| Buffer Init  : {self.buffer_init}')
        out.append(f'| Subsnaping   : {self.subsnap}')
        out.append(f'| Initial N    : {self.__access_tn_buffer__(0, len)}')
        out.append(f'| Final N      : {self.__access_tn_buffer__(-1, len)}')
        out.append(f'|---------------------------')
        return '\n'.join(out)
