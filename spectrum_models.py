#Functions for generating spectra and LyA luminosities according to different models

import numpy as np
import pylab as pl
from scipy.integrate import simps

#Helper stuff----

lya_wavel = 1215.67
c = 3.e5

def gaussian(x, mu, sigma):
	''' Regular Gaussian without normalization '''
	return np.exp(-(x-mu)**2/(2.*sigma**2))

def gaussian_minus_gaussian(x, sigma1, sigma2, mu=lya_wavel):
	f = gaussian(x,mu, sigma1)-gaussian(x,mu,sigma2)
	return f

def get_transmitted_fraction(emission, transmission, wavel):
	emitted =  simps(emission, wavel)
	transmitted = simps(emission*transmission, wavel)
	return transmitted/emitted

#Line models----

def get_line_double_gaussian(mass, wavel):
	''' Gaussian-minus-gaussian model with
	the two sigmas fit to spectra in modelfit.py
	mass is log(Mh/Ms) '''

	sigma1 = -6.5 + 0.75*mass
	sigma2 = -3.2 + 0.35*mass

	return gaussian_minus_gaussian(wavel, sigma1, sigma2)

def get_line_simple_gaussian(wavel, width=150):
	''' Just a Gaussian with fixed width (given in km/s)'''
	sigma = np.sqrt((1+width/c)*lya_wavel - lya_wavel)

	return gaussian(wavel, lya_wavel, sigma)

def get_line_varying_gaussian(mass, wavel):
	''' Gaussian with a line width depending on halo mass '''
	width = 150*((10**mass)/1e10)**(1./3.)
	return get_line_simple_gaussian(wavel, width)

def get_line_spherically_symmetric(wavel):
	''' Analytical solution for a spherically symmetric 
	hydrogen distribution. See Dijkstra et al 2006 '''

	T = 1.e4
	DnuD = 1.057e11*(T/1.e4)**(0.5)
	A21 = 6.3e8
	a = A21/(4*np.pi*DnuD)
	tau_0 = 1.e7 #Typical value
	nu_0	= 2.46607e15
	c		= 2.99792458e8 #m/s
	nu = c/(wavel/1.e10)
	x = (nu-nu_0)/DnuD
	return np.sqrt(np.pi)/(np.sqrt(24.)*a*tau_0)*x**2/(1.+np.cosh(np.sqrt(2.*np.pi**3/27.)*np.abs(x**3)/(a*tau_0)))

#Luminosity models ----
def get_lum_scatter(mass,sigma=0.4):
	''' From fit in fit_mass_to_light.py '''
	#lum = mass+31.9+np.random.normal(0,0.4, len(mass)) #This is the value when fitting to z=7
	lum = mass+31.7+np.random.normal(0,sigma, len(mass)) #This is from fitting to z=6
	if len(lum) == 1:
		return lum[0]
	return lum

def get_uv_lum_scatter(mass):
	''' From fit in fit_mass_to_light.py '''
	#lum = mass+17.2+np.random.normal(0,0.3, len(mass))
	lum = mass+16.9+np.random.normal(0,0.3, len(mass))
	if len(lum) == 1:
		return lum[0]
	return lum
