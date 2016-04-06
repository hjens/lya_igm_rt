About this package
==================
This package contains a number of scripts to calculate the visibility of Lyman-alpha emitters (LAEs) through the intergalactic medium (IGM). The main part of the code is called SimpleTransfer, and is a simplified and parallelized version of Peter Laursen's IGMtransfer (http://adsabs.harvard.edu/abs/2010arXiv1012.2886L). It takes away some of IGMtransfer's features, such as support for an adaptive mesh, and adds some new capabilities such as the possibility to specify sightline directions and take advantage of periodic boundary conditions.

The code takes as input boxes containing the density and velocities of neutral hydrogen in the IGM, along with positions of LAEs. It then calculates the transmission function of Lyman-alpha along some specified sightline directions for each halo. For more information about how these calculations are done, see Laursen 2010 (link above). 

Given the Lyman-alpha transmission functions, one can then calculate the actual transmitted Lyman-alpha line shape, given some assumed intrinsic line shape.

Installation
============
1. Download the files from github
2. Run `make` in the main directory
