#include <iostream>
#include "Simulation.h"
using namespace std;


int main(int argc, char **argv)
{
#ifdef _NO_VEL_
	cout << "Velocities are ignored" << endl;
#endif
	Simulation sim;
	sim.Prepare(argv[1]);
	sim.RunSim();
	cout << "Done" << endl;
	return 0;
}
