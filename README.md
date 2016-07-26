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


Running from a script
---------------------
Coming soon


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

Sightline directions
--------------------
