Overview
==================
This package contains a number of scripts to calculate the
visibility of Lyman-alpha emitters (LAEs) through the
intergalactic medium (IGM), using output from C2-Ray/CubeP3M.
The main part of the code is
called SimpleTransfer, and is a simplified and parallelized
version of Peter Laursen's IGMtransfer
(http://adsabs.harvard.edu/abs/2010arXiv1012.2886L).
It takes away some of IGMtransfer's features, such as
support for an adaptive mesh, and adds some new capabilities
such as the possibility to specify sightline directions and
take advantage of periodic boundary conditions.

SimpleTransfer takes as its input boxes containing the density
and velocities of neutral hydrogen in the IGM, along with
positions of LAEs. It then calculates the transmission function
of Lyman-alpha along some specified sightline directions for
each halo. For more information about how these calculations
are done, see Laursen 2010 (link above).

Given the Lyman-alpha transmission functions, one can then
calculate the actual transmitted Lyman-alpha line shape,
given some assumed intrinsic line shape.

Package contents
================
This package contains several components for calculating and
analyzing Lyman-alpha radiative transfer through the IGM:

* `SimpleTransfer`, which is the main code for calculating
Lyman-alpha transmission functions.
* `MakeCelldata`, which is a program to combine density, velocity
and ionization fraction files from C2-Ray/CubeP3M into a single
file that `SimpleTransfer` can read.
* `make_galdata.py`, which is a small script to convert halo
files into data that `SimpleTransfer` can read.
* `process_output.py`, which contains functions for post-
processing the output from `SimpleTransfer`. It allows for
calculation of the transmitted fraction of Lyman-alpha given
several different intrinsict line models.
* `run_rt.py` which contains functions for running the entire
pipeline. This file can be used as a stand-alone script, or
imported into your own Python code for greater control and
scripted runs.

Prerequisites
=============
* Python, with `numpy` and `scipy` installed.
* `c2raytools`
* A C++ compiler
* A Fortran compiler

Installation
============
1. Download the files from github
2. Run `make` in the main directory


Unfinished parts
================
The code to read halo files from CubeP3M and convert them into
galdata files (that SimpleTransfer can read) still has to be written.
Ideally, there should be a binary file format that contains both
the halo data and the metadata about what the columns contain and
in which units.

Once such a file format exists, the function `get_halodata_from_cubep3m`
can be filled in. This function is in the file `make_galdata.py`.


Usage
=====
Running the full pipeline
-------------------------
To run the full pipeline you need only create a text file containing
the relevant parameters for the simulation and run

```
>>> python run_rt.py my_settings_file.txt
```

A sample settings file (called `sample_settings.txt`) is included
in the package. For more information about each parameter, see
the section called _Parameters_ below).

This will read the specified density, velocity and ionization 
fraction files and combine them into a single file. It will then
make a file containing galaxy data and run the LyA radiative transfer
through the IGM. Finally, it will run the postprocessing. All steps
are controlled by parameters in the given settings file.

Running from a script
---------------------
If you need more control over the process -- for example if you
want to run several radiative transfer simulation steps on the same
input, or if you want to run only the postprocessing step -- you can
run each step in the pipeline from a python script. To do this, first
import the appropriate module:

```
import run_rt
```

Then, use the functions `run_make_celldata`, `run_make_galdata`, 
`run_simpletransfer` and `run_postprocessing`. These functions take 
a dictionary containing simulation parameters as their only argument.
To see the format of this dictionary, look at the function
`get_default_params` in `run_rt.py`.


Configuration
=============
Parameters
----------
Below is a list of all the parameters that can be set to
configure the simulation. The most important ones are all
the filenames (input and output), and the redshift.

**You must also set the correct values for `n_box` and
 `boxsize`.** These are specific to each C2-ray and CubeP3M
 simulation. If you run with the wrong values, everything
 will appear to work, but the results will be wrong.

* `output_dir` - The directory where the output files will
be placed.
* `velocity_file` - The full path to the velocity file.
* `density_file` - The full path to the density file.
* `xfrac_file` - The full path to the ionization fraction
file.
* `redshift` - The redshift of the simulation.
* `raw_output` - The file name of the raw output file from SimpleTransfer (will be placed in `output_dir`).
* `fractions_output` - The name of the file containing
transmitted LyA fractions, from `process_output.py` (will be placed in `output_dir`).
* `tau_output` - The name of the file containing tau as a function of
wavelength for each sightline traced.
* `line_model` - The model to use for the intrinsic LyA
emission. Default is 'gmg'. See section below for more
information.
* `start_dist_vr` - The distance from galaxies, in virial
radii, where the radiative transfer starts. Default is 1.5.
* `specres_bins` - The spectral resolution of the
transmission functions, measured in number of bins. Default
is 1500.
* `wavel_lower` - The wavelength, in Angstrom, where the
radiative transfer begins. Default is 1180.
* `wavel_upper`  - The wavelength, in Angstrom, where the
radiative transfer stops. Default is 1220.
* `num_los` - Number of sightlines to trace for each galaxy.
See section below for more information.
* `num_sightlines_between_writes` - The number of sightlines
traced between each write. Default is 10000. You usually do
not need to change this.
* `frac_total_radius` - The fraction of the total volume
used for ray tracing. Default is 2.0. You usually do not need
to change this.
* `hubble_const` - The Hubble constant. Default is 70.
* `omega_m` - Omega_M. Default is 0.27.
* `omega_0` - Omega_0. Default is 0.73.
* `los_dir` - The line-of-sight directions. Default is 'x'.
See section below for more information.
* `n_box` - The fine resolution used in CubeP3M.
* `boxsize` - The size of the box in Mpc/h.
* `overwrite_output` - If this is True, any files in the
output directory will be overwritten. Default is False.


Line models
-----------
SimpleTransfer only calculates the transmission function of LyA
through the IGM. To calculate the transmitted fraction of LyA, you
must specify some intrinsic line model. A few models are 
provided in `spectrum_models.py` (see Jensen et al 2013 for more
information):
* gmg (Gaussian-minus-Gaussian)
* gaussian (single Gaussian with fixed width)
* gaussian_varying (single Gaussian with width depending on halo mass)
* analytic_sphsym (analytic solution, spherically symmetric)

In addition, if you run the post-processing step from a script, you may
supply your own line model as a parameter. In this case, the 
`line_model` parameter must be a function accepting one argument, the
log10 mass of the halo.


Sightline directions
--------------------
The parameters file contains an entry called `los_dir`, which
specifies the direction(s) of the lines-of-sight. This parameter
is a string which can either be 'x', 'y' or 'z' or the name of
a file. If it is 'x', 'y' or 'z', all sightlines will be traced
along the specified coordinate axis. 

If a filename is instead
specified, the sightlines will be read from the file. Each line
in the file must contain three numbers, specifying a direction vector.
For example, the following file will trace sightlines along all
three coordinates axes, in both positive and negative directions:

```
1.0 0.0 0.0
-1.0 0.0 0.0
0.0 1.0 0.0
0.0 -1.0 0.0
0.0 0.0 1.0
0.0 0.0 -1.0
```
