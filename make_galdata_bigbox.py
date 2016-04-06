import numpy as np
import os
import c2raytools as sim
import sys
sys.path.append('/home/hjens/workspace/LyA_bigbox/src')
import halofile_tools as lya
#import lya_tools as lya

sim.conv.set_sim_constants(425.)

#Read the config file, selection critera
selection_criteria = {}
f = open('/home/hjens/LyA_bigbox/halo_criteria.txt', 'r')
for line in f.readlines():
	selection_criteria[line.split('=')[0].strip()] = float(line.split('=')[1].strip())
f.close()



outfile = 'halos.dat'
min_mass = selection_criteria['min_mass']#1e10
max_mass = selection_criteria['max_mass']#3e10
max_number = selection_criteria['max_number']#30
print 'Min mass = ', min_mass
print 'Max mass = ', max_mass
print 'Max number = ', max_number
settingsfile = open('/home/hjens/LyA_bigbox/settings.txt', 'r')
z = float(settingsfile.readlines()[5].split('=')[1])
settingsfile.close()
infile = '/home/hjens/links/c2ray/425Mpc_WMAP5/halos/%.3fhalo.dat' % z
if not os.path.exists(infile):
	print 'File ', infile, ' does not exist, looking in local instead'
	#infile = '/home/hjens/links/local/ranger_halos/%.3fhalo.dat' % z
	#infile = '/home/hjens/links/local/slask/bigbox_halos_unshifted/%.3fhalo.dat' % z
	infile = '/disk/sn-12/hjens/Halolistsbin_425/%.3fhalo.dat' % z

#Conversion stuff. IGMtransfer needs everything in PROPER coordinates
pbox = sim.conv.LB/(1.+z) #Box length in proper coordinates
lscale =  pbox/float(sim.conv.nbox_fine) #    proper size of a (cubep3m) cell in Mpc
tscale = 2.0/(3.0*np.sqrt(sim.const.Omega0)*sim.const.H0/sim.const.Mpc*sim.const.kms*(1+z)**2) # time scale in s (H0=100*h)
gridpos_to_kpc = lambda x : (x * lscale - pbox/2)*1.e3
gridlength_to_kpc = lambda r : r * lscale*1.e3
simvel_to_kms = lambda v : v * lscale*sim.const.Mpc/tscale/sim.const.kms #proper velocity

print 'Cube side is ', pbox*1.e3/2
print 'z ', z
print 'LB ', sim.conv.LB

#For testing
def mvir(r, sigma):
	'''virial mass in solar masses for r kpc, sigma km/s '''
	return (5 * (sigma*1.e3)**2 * r*3.08568025e19 / 6.67e-11 ) / 1.989e30

#Read input file
hlist = sim.HaloList(infile, min_mass, max_select_mass = max_mass, max_select_number=max_number)
print 'Read ', len(hlist.halos), ' haloes with mass greater than ', min_mass, ' solar masses.'

#Read halo offsets
shifts = lya.get_halo_shifts(z)

#Convert to arrays
x_pos = gridpos_to_kpc(np.array([h.pos[0]-shifts[0] for h in hlist.halos]))
y_pos = gridpos_to_kpc(np.array([h.pos[1]-shifts[1] for h in hlist.halos]))
z_pos = gridpos_to_kpc(np.array([h.pos[2]-shifts[2] for h in hlist.halos]))
radii = gridlength_to_kpc(np.array([h.r for h in hlist.halos]))
x_vel = simvel_to_kms(np.array([h.vel[0] for h in hlist.halos]))
y_vel = simvel_to_kms(np.array([h.vel[1] for h in hlist.halos]))
z_vel = simvel_to_kms(np.array([h.vel[2] for h in hlist.halos]))
mass = np.array([h.solar_masses for h in hlist.halos])


#TODO-----
print 'TODO: apply periodic boundary conditions!!!!'
#----

#---
#Remove the ones < 15 kpc from the edge
cube_side = pbox*1.e3/2-40
print np.where(z_pos > cube_side)
rem = np.where((x_pos < -cube_side) | (x_pos > cube_side) | (y_pos < -cube_side) | (y_pos > cube_side) | (z_pos < -cube_side) | (z_pos > cube_side)) 
print 'Removing ', len(rem[0]), ' halos'
print 'cube_side:', cube_side
x_pos = np.delete(x_pos, rem[0])
y_pos = np.delete(y_pos, rem[0])
z_pos = np.delete(z_pos, rem[0])
radii = np.delete(radii, rem[0])
x_vel = np.delete(x_vel, rem[0])
y_vel = np.delete(y_vel, rem[0])
z_vel = np.delete(z_vel, rem[0])
mass = np.delete(mass, rem[0])
print np.where(z_pos > cube_side)
---


#Convert velocity to account for expansion
dx = (x_pos*1e-3) #Just convert these to Mpc
dy = (y_pos*1e-3)
dz = (z_pos*1e-3)
Hz = sim.const.H0*np.sqrt(sim.const.Omega0*(1.0+z)**3+sim.const.lam)
x_vel += dx*Hz
y_vel += dy*Hz
z_vel += dz*Hz


#Write output
file = open(outfile, 'w')
file.write('# x \t y \t z \t r_vir \t v_x \t v_y \t v_z \t log10(M) \n')
file.write('#----------------------------------------------------------------------\n')
file.write('#kpc \t kpc \t kpc \t kpc \t km/s \t km/s \t km/s \t log10(solar mass)\n')
file.write('#----------------------------------------------------------------------\n')
for i in xrange(len(x_pos)):
	file.write('%.5f \t %.5f \t %.5f \t %.5f \t %.5f \t %.5f \t %.5f \t %.5f\n' % 
	(x_pos[i], y_pos[i], z_pos[i], radii[i], x_vel[i], y_vel[i], z_vel[i], np.log10(mass[i])))

file.close()

