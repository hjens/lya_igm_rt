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


Usage
=====
Running the full pipeline
-------------------------
Coming soon
