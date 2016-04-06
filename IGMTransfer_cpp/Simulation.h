#include "SimParams.h"

class Simulation
{
	public:
		Simulation();
		~Simulation();

		void Prepare(string configfile);
		void RunSim();
		void RunSimPart(int firstgal, int lastgal, int first_in_chunk);
	private:
		void InitFreq(Vector3d nhat, double *x, Vector3d pos, Vector3d U_sys);
		void Sigma(double *x, double *sigma_x, Vector3d pos);
		void LorentzTransform(double *x, Vector3d nhat, Vector3d oldPos, Vector3d newPos);
		void WriteData(string filename, int ngals);
		void WriteDataHeader(string filename);
		void WriteDataEnd(string filename);
		SimParams *params;
		float **tau_out;
#ifdef _OUTPUT_ALL_THE_THINGS_
		ofstream all_stream;
#endif
};

//Workaround to use pthread with classes
struct ThreadData
{
	int firstgal, lastgal, first_in_chunk;
	Simulation *sim;
};
void *start_thread(void *data);
