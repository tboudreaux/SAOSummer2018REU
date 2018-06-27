import pandas as pd
import os
import re

class lagr_base:
    def __init__(self, path):
        self.path = path
        self.df, self.names = self.load(self.path)

    def load(self, lagr):
        with open(lagr, 'r') as f:
            lagr_lines = f.readlines()
        header_line = lagr_lines[0]
        names, macrolabels = self.__build_header__(header_line)
        df = pd.read_csv(lagr, sep=r'\s+', engine='python', names=names, skiprows=2)
        return df, names


    @staticmethod
    def __build_header__(raw_header):
        parsed_header = [x.split() if len(x.split()) != 1 else x.split('<') for x in re.split(r'\s{2,}', raw_header.split(':')[1])[1:]]
        
        line_starts = [int(x[0]) for x in parsed_header]
        line_starts.insert(0, 1)
        line_starts.insert(-1, 285)
        line_labels = [x[1].strip('<').strip('>').strip('\\') for x in parsed_header]
        line_labels.insert(0, 'Time')

        full_labels = list()

        for start, end, label in zip(line_starts, line_starts[1:], line_labels):
            lines = [f"{label}_{i}" for i, n in enumerate(range(start, end))]
            full_labels.extend(lines)

        return full_labels, line_labels

    def __getitem__(self, key):
        keyed_names = list()
        keyed_names.extend([x for x in self.names if key in x])

        return self.df[keyed_names]

    def __repr__(self):
        out = list()
        out.append(f'|---------------------------')
        out.append(f'| lagr length  : {len(self.df)}')
        out.append(f'| lagr rows    : {len(self.df.columns)}')
        out.append(f'|---------------------------')
        return '\n'.join(out)








