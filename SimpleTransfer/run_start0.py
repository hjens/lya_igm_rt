import os
import sys

z = float(sys.argv[-1])
#for z,node in zip([6.905, 7.059, 7.391, 7.570, 7.760, 7.960], [15, 16, 17, 18, 19, 20]):
olddirname = '/disk/sn-12/hjens/Lumfunc_simpletransfer_big/z%.3f_1e10up_coordaxes_rand' % z
newdirname = '/disk/sn-12/hjens/Lumfunc_simpletransfer_big/z%.3f_1e10up_coordaxes_rand_start0' % z
newfilename = '/disk/sn-12/hjens/Lumfunc_simpletransfer_big/z%.3f_1e10up_coordaxes_rand_start0.in' % z
os.system('mkdir %s' % newdirname)
os.system('cp %s/GalData.dat %s' % (olddirname,newdirname))
os.system('cp %s/CellData.bin %s' % (olddirname,newdirname))
os.system('./SimpleTransfer.x %s' % newfilename)
