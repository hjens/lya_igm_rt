#Compare two output files like a unit test, to see that refactoring works
import numpy as np
import pylab as pl
import sys
sys.path.append('/home/hjens/IGMTransfer')
import PyProcessIGM as ppi

ppi.read_igmtransfer_config('/disk/sn-12/hjens/TestSimpletransfer/z7.480_testmanyhalos_hires.in')
tau_new = ppi.read_igmtransfer_data(ppi.datafile_name)

ppi.read_igmtransfer_config('/disk/sn-12/hjens/TestSimpletransfer/z7.480_testmanyhalos_hires_ref.in')
tau_ref = ppi.read_igmtransfer_data(ppi.datafile_name)

pl.plot(tau_new-tau_ref)
pl.ylabel('new-ref')
pl.show()
