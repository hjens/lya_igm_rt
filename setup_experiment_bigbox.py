#Functions to create input files for SimpleTransfer and data files from C2Ray data
#If run as a standalone application, this script will ask you for simulation parameters and prepare and run an IGMtransfer simulation

def read_parameter(prompt, default_value = None):
	msg = prompt + ': '
	if default_value:
		msg = prompt + ' [' + str(default_value) + ']:'
	try:
		value = input(msg)
	except:
		print 'Invalid or no value. Setting to ' + str(default_value)
		value = default_value
	return value
	


def run_simulation(experiment_name = 'Bigbox', sim_z = 8.515, sim_distvr = 1.5, 
	sim_name = None, sim_res = 1200, sim_lw = 1180, sim_hw = 1225, sim_los = 1000, min_halo_mass = 1e10, max_halo_mass = 2e10, max_halos = 30, los_dir='x', cleanup = True):

	igmtransfer_dir = '/home/hjens/IGMTransfer_cpp/'
	output_dir = '/disk/sn-12/hjens/'

	#**************Create the simulation input file*******************
	print '\n******Making input file************'
	if sim_name == None:
		sim_name = 'z%.3f_res%d_los%d' % (sim_z, sim_res, sim_los)
	sim_input_filename = output_dir + experiment_name + '/' + sim_name + '.in'
	import os
	try:
		os.mkdir(output_dir + experiment_name + '/' + sim_name)
	except: #Directory already exists
		pass
	print 'Writing simulation configuration file:', sim_input_filename
	infile = open(sim_input_filename, 'w')
	infile.write('\''+output_dir+experiment_name+'\' \t #Name of directory containing the data subdirectory\n')
	infile.write('\''+sim_name+'\' \t# Name of subdirectory containing data to be read (and written) \n')
	infile.write('\'CellData.bin\' \t #File containing cell parameters\n')
	infile.write('\'GalData.dat\' \t #File containing galaxy parameters\n')
	infile.write('\''+output_dir+experiment_name+'\' \t #Directory containing subdirectory for reading\n')
	infile.write('\'%s.bin\' \t #File containing cell parameters\n' % sim_name)
	infile.write('\'%sproc.dat\' \t #File containing galaxy parameters\n' % sim_name)
	infile.write(str(sim_z)+'\t# Redshift of snapshot\n')
	infile.write(str(sim_distvr)+'\t# Distance in virial radii from galaxy centers to start sightlines\n')
	infile.write(str(sim_res) + '\t #Spectral resolution in bins\n')
	infile.write(str(sim_lw) + ' ' + str(sim_hw) + '\t#Lower and upper value of wavelength interval in Angstrom\n')
	infile.write('1180. 1220. \t#Lower and upper value of wavelength interval in which to calculate statistics Angstrom\n')
	infile.write(str(sim_los) + '\t# Number of sightlines per galaxy\n')
	infile.write('10000\t# Number of sightlines traced between each write\n')
	infile.write('2.0\t # Fraction of total radius to be used for the IGM RT\n')
	infile.write('70.\t             # Hubble constant in km/s/Mpc\n')
	infile.write('.27\t# Matter density fraction\n')
	infile.write('.73\t# Cosmological constant density fraction\n')
	infile.write('%s\t#Direction of LOS. \'x\', \'y\', \'z\' or filename containing (x,y,z) directions\n' % los_dir)
	infile.close()
	#******************************************************************

	#***********Create CellData****************************************
	print '\n********Making CellData file**************'
	settings = open('settings.txt', 'w')
	settings.write('&settings\n')
	settings.write('vfile=\'/disk/dawn-1/garrelt/Reionization/C2Ray_WMAP5/425Mpc_WMAP5/coarser_densities/%.3fv_all.dat\'\n' % sim_z)
	settings.write('dfile=\'/disk/dawn-1/garrelt/Reionization/C2Ray_WMAP5/425Mpc_WMAP5/coarser_densities//%.3fn_all.dat\'\n' % sim_z)
	settings.write('xfile=\'/disk/dawn-1/garrelt/Reionization/C2Ray_WMAP5/425Mpc_WMAP5/f2_10S_504/results/xfrac3d_%.3f.bin\'\n' % sim_z)
	settings.write('outfile=\'' + output_dir +experiment_name+'/'+sim_name+'/CellData.bin\'\n')
	settings.write('redshift=%.3f\n' % sim_z)
	settings.write('/')
	settings.close()
	os.system('./make_celldata.x')
	
	#***********Create GalData****************************************
	print '\n********Making GalData file**************'
	halo_file = open('halo_criteria.txt', 'w')
	halo_file.write('min_mass = %f\n' % min_halo_mass)
	halo_file.write('max_mass = %f\n' % max_halo_mass)
	halo_file.write('max_number = %f\n' % max_halos)
	halo_file.close()
	os.system('python make_galdata_bigbox.py')
	os.system('mv halos.dat %s' % (output_dir + experiment_name+ '/' + sim_name + '/GalData.dat'))

	#******************************************************************

	#***********Run RT****************************************
	print '\n********Running IGMtransfer**************'
	os.chdir(igmtransfer_dir)
	os.system('./SimpleTransfer.x '+ output_dir + experiment_name + '/' + sim_name + '.in')
	if cleanup:
		print '\n*******Cleaning up**********'
		os.system('rm ' +  output_dir + experiment_name+ '/' + sim_name + '/CellData.bin')
		#os.system('rm ' +  experiment_name+ '/' + sim_name + '/GalData.dat')
	#print '\n********Postprocessing**************'
	#os.system('./ProcessIGM.x < ' + output_dir + experiment_name + '/' + sim_name + '.in')

	#**********Run plotting and analysis***************************
	#print '\n************Plotting and analyzing********************'
	#os.system('python /home/hjens/IGMTransfer/PyProcessIGM.py ' + output_dir + experiment_name + '/' + sim_name +'.in')
	#os.system('python /home/hjens/LyA_bigbox/PyProcessIGM_gmg.py ' + output_dir + experiment_name + '/' + sim_name +'.in')
	os.chdir('../LyA')

	

if __name__ == '__main__':
	import sys
	if len(sys.argv) >= 2 and sys.argv[-1] != '-f':
		print 'Reading ', sys.argv[-1], '...'
		param_file = open(sys.argv[-1])
	else:
		print 'No input file given. Reading experiment_bigbox.txt...'
		param_file = open('experiment_bigbox.txt')
	lines = param_file.readlines()
	param_file.close()
	params = {}
	for line in lines:
		param, value = [s.strip() for s in line.split('#')[0].split('=')]
		params[param] = value
		print param, '=', value

	if '-f' in sys.argv:
		cont = 'y'
	else:
		cont = ''
	while cont.lower() != 'y' and cont.lower() != 'n':
		cont = raw_input('----Continue? [Y/N] -----\n')
	if cont == 'n':
		sys.exit()

	run_simulation(experiment_name = params['experiment_name'], 
			sim_z = float(params['sim_z']), 
				sim_distvr = float(params['sim_distvr']), 
				sim_name = params['sim_name'], 
				sim_res = int(params['sim_res']), 
				sim_lw = float(params['sim_lw']), 
				sim_hw = float(params['sim_hw']), 
				sim_los = int(params['sim_los']), 
				min_halo_mass = float(params['min_halo_mass']), 
				max_halo_mass = float(params['max_halo_mass']), 
				max_halos = float(params['max_halos']),
				los_dir=params['los_dir'], 
				cleanup = int(params['cleanup']))

