'''
Created on Mar 14, 2013

@author: Hannes Jensen

Tools for reading binary halo files
The columns of the files are:
x, y, z, r, m
Positions are in proper kpc, origin in the box center
radii are in proper kpc
masses in log10(Msol)
'''

import numpy as np
import common_paths
import os

def read_halos(filename):
    ''' Read  binary halo file
    Return the raw data array '''
    
    data = np.fromfile(filename, dtype='float32')
    n_cells = len(data)
    data = data.reshape((n_cells/5,5))
        
    return data


def read_halos_from_z(z, path = None):
    ''' Read binary halo file
    assuming standard file name convention
    '''
    
    if path == None:
        path = common_paths.bigbox_halo_path
        
    filename = '%.3fhalo.bin' % z

    full_file = os.path.join(path, filename)
    return read_halos(full_file)


def read_halos_from_z_1e10up(z, path=None):
    '''
    Same as read_halos_from_z but read one of the files
    with only M>10^10
    '''
    if path == None:
        path = common_paths.bigbox_halo_path
        
    filename = '%.3fhalo_1e10up.bin' % z

    full_file = os.path.join(path, filename)
    return read_halos(full_file)


def get_halo_shifts(z, shifts_file=None):
    '''
    Return the random offsets for the halo files
    '''
    
    if shifts_file == None:
        shifts_file = common_paths.bigbox_shifts_file
    shifts = np.loadtxt(shifts_file)
    shifts_z = shifts[:,0]
    idx = np.argmin(np.abs(shifts_z-z))
    return shifts[idx,1:]


def read_galdatafile(filename):
    '''
    Read an input file for IGMtransfer
    The results will contain x,y,z,m
    '''
    galdata = open(filename, 'r')
    gallines = galdata.readlines()[4:]
    galdata.close()
    data = np.zeros((len(gallines),5))
    data[:,0] = np.array([float(l.split()[0]) for l in gallines]) #x
    data[:,1] = np.array([float(l.split()[1]) for l in gallines]) #y
    data[:,2] = np.array([float(l.split()[2]) for l in gallines]) #z
    data[:,3] = np.array([float(l.split()[3]) for l in gallines]) #r
    data[:,4] = np.array([float(l.split()[-1]) for l in gallines]) #m
    
    return data
