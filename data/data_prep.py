import pandas as pd
import numpy as np
import os, sys

def data_prep(target):
    '''Designed for use by LT Spencer Kitten in preparation of thesis completion, modificaiton needed on other computers.'''
    start = 'C:\\Users\\spenc\\Documents\\GitHub\\Thesis\\data'
    rootdir = start + target

    os.chdir(rootdir)
    columns = ['n_targets', 'n_merchants', 'n_submarines', 'seeds', 'max_samples','speed_sub','P_k','Lam_T','Lam_M', 'speed_target']
    parameters = pd.read_csv('test-jobs.csv', index_col= 0, header = None)
    outfile = pd.DataFrame()

    for filename in os.listdir(rootdir):
        f = os.path.join(rootdir, filename)

        # checking to ensure experiment file
        if (f[-5] != 's') & os.path.isfile(f):
            KTdf = pd.read_csv(f,index_col= None)
            KTdf.drop('Unnamed: 0',axis = 1, inplace = True)
            KTdf.astype(float)
            KTdf = KTdf.mean(axis = 0)
            working = parameters.loc[int(f[74:-4])]
            working.index = columns
            out = pd.concat([KTdf.T, working.T],axis = 0)

        outfile = pd.concat([outfile, out],axis = 1)

    outfile.columns = list(range(1,len(outfile.columns)+1))
    outfile = outfile.T
    outfile.drop(outfile.tail(2).index,inplace = True)
    outfile.to_csv('outfile_%s.csv' % target[1:])

    os.chdir(start)
    return

if __name__ == '__main__':
    target = sys.argv[1]
    target = "\\" + str(target)
    data_prep(target)
