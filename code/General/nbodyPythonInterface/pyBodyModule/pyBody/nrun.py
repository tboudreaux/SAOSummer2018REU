import pandas as pd
import numpy as np
import os


from .snapshot import snapshot_set

class nbodyRun:
    def __init__(self, path, subsnap=False):
        self.snapset = snapshot_set(path)
        path = (path[:-1] if path[-1]=="/" else path)
        csp_old = f"{path}/cluser_status.csv"
        csp_new = f"{path}/cluster_status.csv"

        assert os.path.exists(csp_old) or os.path.exists(csp_new)

        csp, self.new = ((csp_new, True) if os.path.exists(csp_new) else (csp_old, False))
        self.cluster_status = pd.read_csv(csp, sep=r"\s+", engine="python")

    def cluster_drift(self, start=0, stop=-1):
        pos_i = np.array([self.cluster_status['RG1'].iloc[start],
                 self.cluster_status['RG2'].iloc[start],
                 self.cluster_status['RG3'].iloc[start]])
        pos_f = np.array([self.cluster_status['RG1'].iloc[stop],
                 self.cluster_status['RG2'].iloc[stop],
                 self.cluster_status['RG3'].iloc[stop]])
        return pos_f - pos_i

    def mass_change(self, start=0, stop=-1):
        if not self.new:
            raise EnvironmentError('Old version of run detected, cluser_status vs cluster_status')
        m_i = self.cluster_status['ZMASS'].iloc[start]
        m_f = self.cluster_status['ZMASS'].iloc[stop]
        return m_f - m_i


    def __repr__(self):
        out = list()
        out.append(f'|===========================')
        out.append(f'| Snapset data:')
        out.append(str(self.snapset))
        out.append(f'| Cluster Status:')
        out.append(f'|---------------------------')
        out.append(f'| Delta Pos    : {self.cluster_drift()}')
        if self.new:
            out.append(f'| Delta Mass   : {self.mass_change():0.2f}')
        out.append(f'|---------------------------')
        out.append('|===========================')
        return '\n'.join(out)