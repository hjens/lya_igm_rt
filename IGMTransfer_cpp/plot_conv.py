import pylab as pl
import numpy as np
import sys
sys.path.append('/home/hjens/IGMTransfer')
import PyProcessIGM as ppi
import gaussian_line as g

datadir = '/disk/sn-12/hjens/Simpletransfer_convtest/z7.480_coordaxes_cell'

pl.figure()
fignum = 1
for stepdiv in [1,2,5,10,50]:
	infile = datadir+'%d.in' % stepdiv
	ppi.read_igmtransfer_config(infile)
	tau = ppi.read_igmtransfer_data(ppi.datafile_name)
	if fignum==1:
		print tau

	pl.subplot(5,1,fignum); fignum+=1
	pl.text(1196,0.6,'Celldiv %d' % stepdiv)
	for i in range(4*3):
		pl.plot(ppi.wavel, np.exp(-tau[i,:]))
	pl.xlim([1195,1223])

pl.figure()
fignum = 1
for step1,step2 in zip([1,2,5,10],[2,5,10,50]):
	print step1, step2
	infile = datadir+'%d.in' % step1
	ppi.read_igmtransfer_config(infile)
	tau1 = ppi.read_igmtransfer_data(ppi.datafile_name)

	infile = datadir+'%d.in' % step2
	ppi.read_igmtransfer_config(infile)
	tau2 = ppi.read_igmtransfer_data(ppi.datafile_name)

	pl.subplot(4,1,fignum); fignum+=1
	pl.text(1196,-0.4,'%d minus %d' % (step2,step1))
	for i in range(4*3):
		pl.plot(ppi.wavel, np.exp(-tau2[i,:])-np.exp(-tau1[i,:]))
	pl.xlim([1195,1223])
	pl.ylim([-0.8,0.1])

#Highres
ppi.read_igmtransfer_config('/disk/sn-12/hjens/Simpletransfer_convtest/z7.480_coordaxes_highres_cell10.in')
tau_highres = ppi.read_igmtransfer_data(ppi.datafile_name)
ppi.read_igmtransfer_config('/disk/sn-12/hjens/Simpletransfer_convtest/z7.480_coordaxes_cell50.in')
tau_lowres = ppi.read_igmtransfer_data(ppi.datafile_name)
pl.figure()
gauss = g.lya_gaussian(ppi.wavel)
los_num = 1
pl.plot(ppi.wavel, np.exp(-tau_highres[los_num,:]), label='highres')
pl.plot(ppi.wavel, np.exp(-tau_lowres[los_num,:]), label='lowres')
pl.plot(ppi.wavel, gauss*np.exp(-tau_highres[los_num,:]), label='hr trans')
pl.plot(ppi.wavel, gauss*np.exp(-tau_lowres[los_num,:]), label='lr trans')
pl.legend(loc=0)
pl.xlim([1195,1225])

pl.show()
