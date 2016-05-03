import numpy as np
import sys
import os
import pylab as pl
sys.path.append('/home/hjens')
sys.path.append('/home/hjens/links/local/LineModel')
import struct
import spectrum_models as sm
read_int = lambda f: struct.unpack('i', f.read(4))[0] 

#-----Parameters-----
read_in_chunks = True
#--------------------

def get_good_n_chunks(n_gal, nmax = 1000, nmin = 1):
	''' Find a suitable integer that divides n_gal into an integer number of chunks '''
	for n in range(nmax,nmin,-1):
		if np.mod(n_gal,n) == 0:
			return n
	raise ValueError('Could not find a suitable n_chunks')

def read_igmtransfer_data(datafile_name):
    ''' Read a datafile from IGMtransfer and return the transmitted functions '''
    #Read header
    datafile = open(datafile_name, 'rb')
    dummy = read_int(datafile)
    n_rec = read_int(datafile)
    n_los = read_int(datafile)
    dummy = read_int(datafile)
    print 'Reading data file...'

    #Read each of the records
    ifrac = n_los/n_rec
    recsize = ifrac*specres
    tau_data = np.zeros(n_los*specres, dtype='float32')
    print 'reading'
    for i in range(n_rec):
        dummy = read_int(datafile)
        if i < n_rec-1:
            tau_data[i*recsize:(i+1)*recsize] = np.fromfile(datafile, dtype='float32', count = recsize)
        else:
            tau_data[i*recsize:] = np.fromfile(datafile, dtype='float32', count = n_los*specres-i*recsize)
        dummy = read_int(datafile)
    print 'reshaping'
    tau_data[np.flatnonzero(tau_data != tau_data)] = 1e10 #Try to prevent numerical overflow
    tau_data[np.flatnonzero(tau_data < 0)] = 0. #Try to prevent numerical overflow

    tau_data = tau_data.reshape((n_los,specres))
    return tau_data#np.exp(-tau_data)

def get_transmissions_in_chunks(datafile_name, n_chunks):
	''' Read datafile like above, but do it in chunks, and 
	calculate transmitted fractions on the go.
	Currently supports only n_rec = 1 '''

	#Read the galaxy masses, needed for varying linewidths
	galdata = open(galdata_filename, 'r')
	gallines = galdata.readlines()[4:]
	galdata.close()
	halo_m = np.array( ([float(l.split()[7]) for l in gallines]) )

	T_gmg = [] #Gaussian minus gaussian

	#Read header
	datafile = open(datafile_name, 'rb')
	dummy = read_int(datafile)
	print 'dummy:', dummy
	n_rec = read_int(datafile)
	print 'n_rec:', n_rec
	n_los = read_int(datafile)
	print 'n_los:', n_los
	dummy = read_int(datafile)

	#Get the number of chunks to use
	if n_chunks < 0:
		n_chunks = get_good_n_chunks(n_los)

	print 'Reading data file...'
	ifrac = n_los/n_rec
	recsize = ifrac*specres
	chunk_size = recsize/n_chunks
	print 'n_chunks:', n_chunks
	print 'recsize = ', recsize
	print 'n_los = ', n_los, ', ', num_los, ' per galaxy'
	print 'specres= ', specres
	assert(np.mod(chunk_size,specres) == 0)
	assert(n_rec == 1)
	print 'num halos:', recsize / (num_los*specres)
	dummy = read_int(datafile)
	los_idx = 0

	for chunk in range(n_chunks):
		print 'Reading chunk ', chunk, ' of ', n_chunks
		tau = np.fromfile(datafile, dtype='float32', count=chunk_size)
		tau[np.flatnonzero(tau != tau)] = 1e10 #Try to prevent numerical overflow
		tau[np.flatnonzero(tau < 0)] = 0. #Try to prevent numerical overflow
		tau = tau.reshape((chunk_size/specres, specres))
		T = np.exp(-tau)
		print 'Calculating transmissions...'
		#for i in range(len(halo_m)):
		for i in range(T.shape[0]):
			halo_idx = los_idx/num_los
			spectrum_gmg = sm.line_model_gmg(halo_m[halo_idx], wavel)

			T_gmg.append(sm.get_transmitted_fraction(spectrum_gmg, T[i,:], wavel))
			los_idx+=1

	return np.array(T_gmg)


def read_igmtransfer_config(configfile_name):
	#First read the config file and figure out where the output file is
	global indir, specres, redshift, low, high, subdir, datafile_name, procfile_name, wavel, galdata_filename, num_los
	print 'Reading config file...'
	configfile = open(configfile_name, 'r')
	lines = configfile.readlines()
	configfile.close()
	indir = lines[0].split()[0][1:-1] #The directory of the output
	specres = int(lines[9].split()[0])
	redshift = float(lines[7].split()[0])
	low = float(lines[10].split()[0])
	num_los = int(lines[12].split()[0])
	high = float(lines[10].split()[1])
	subdir = lines[1].split()[0][1:-1]
	datafile_name = lines[5].split()[0][1:-1]
	datafile_name = os.path.join(indir, subdir, datafile_name)
	galdata_filename = lines[3].split()[0][1:-1]
	galdata_filename = os.path.join(indir, subdir, galdata_filename)
	procfile_name = lines[6].split()[0][1:-1]
	procfile_name = os.path.join(indir, subdir, procfile_name)
	wavel = np.linspace(low, high, specres)

if __name__ == '__main__':
	read_igmtransfer_config(sys.argv[1])
	if len(sys.argv) > 2:
		n_chunks = int(sys.argv[-1])
		print 'Using ', n_chunks, ' chunks'
	else:
		n_chunks = -1 #Figure this out ourselves

	T_gmg = get_transmissions_in_chunks(datafile_name, n_chunks=n_chunks)
	T_gmg.tofile(os.path.join(indir, subdir, 'transmitted_fractions_gmg.bin'))


