#include "Simulation.h"
#include "constants.h"
#include <iostream>
#include <fstream>
#include <sys/stat.h>
#include <pthread.h>
#include <sstream>
using namespace std;
//------------------------------------------------------
Simulation::Simulation()
{
	params = new SimParams;
}
//------------------------------------------------------
Simulation::~Simulation()
{
	delete params;
}
//------------------------------------------------------

//Read config files, setup stuff etc
void Simulation::Prepare(string configfile)
{
	params->ReadConfigFile(configfile);
	params->ReadGalData();
	params->ReadCellData();
	params->ReadLOSDir();
}
//------------------------------------------------------

//Main method. Run the simulation
//Run in a number of chunks. Each chunk is run in a number of threads, and then written to file
void Simulation::RunSim()
{
    cout << "Running simulation..." << endl;
    cout << "Total number of galaxies " << params->GetGalaxyCount() << endl;
	int chunk_gals = 1000; //Write data for every so many galaxies
	WriteDataHeader(params->GetOutdataFilename());

	for (int chunk_start = 0; chunk_start < params->GetGalaxyCount(); chunk_start += chunk_gals)
	{
		int chunk_stop = chunk_start+chunk_gals > params->GetGalaxyCount() ? params->GetGalaxyCount() : 
			chunk_start+chunk_gals;
		cout << "Chunk from gal# " << chunk_start << " to " << chunk_stop 
			<< " (tot " << params->GetGalaxyCount() << ")" << endl;
		
		//Init main data array
		tau_out = new float*[(chunk_stop-chunk_start)*params->GetNLOS()];
		
		//Set up threads
		int chunk_num_gals = (chunk_stop-chunk_start);
		int gals_per_thread = ceil((float)chunk_num_gals/(float)cst::max_threads);
		int num_threads = 0; //This might be less than max_threads, if the number of galaxies is low
		pthread_t threads[cst::max_threads];
		ThreadData tdata[cst::max_threads];
		cout << "Total galaxies in chunk: " << chunk_num_gals << endl;
		cout << "Galaxies per thread: " << gals_per_thread << endl;
		cout << "Photon travel distance: " << params->GetDtot() << " kpc " << endl;


		for (int i = chunk_start,t = 0; i < chunk_start+chunk_num_gals; i += gals_per_thread, t++)
		{
			int firstgal = i, 
				lastgal = i+gals_per_thread > chunk_stop ? chunk_stop : i+gals_per_thread;
			cout << "Starting thread from gal " << i << " to " << lastgal << endl;
			tdata[t].sim = this; tdata[t].firstgal = firstgal; tdata[t].lastgal = lastgal;
			tdata[t].first_in_chunk = chunk_start;
			pthread_create(&threads[t], NULL, start_thread, (void*)&tdata[t]);
			num_threads ++;
		}
		//Wait until all threads are done
		void *status;
		for (int i = 0; i < num_threads; i++)
		{
			pthread_join(threads[i], &status);
		}
		cout << "All threads are done." << endl;

		//Write data
		WriteData(params->GetOutdataFilename(), chunk_stop-chunk_start);

		//Free stuff
		cout << "Freeing memory..." << endl;
		for (int i = 0; i < (chunk_stop-chunk_start)*params->GetNLOS(); i++)
		{
			delete[] tau_out[i];
		}
		cout << "done" << endl;
		delete[] tau_out;
	}
	WriteDataEnd(params->GetOutdataFilename());
}
//------------------------------------------------------

//Run a part of the simulation, starting with firstgal and
//up to, but not including lastgal
//first_in_chunk is the first galaxy in this write chunk, used to determine
//where to allocate memory
//Can be run as a thread
void Simulation::RunSimPart(int firstgal, int lastgal, int first_in_chunk)
{
	//Some variables that we will need
	double d_tot = params->GetDtot();
	double dd = params->GetBoxSize()/(double)(10*params->GetMeshSize());
	double boxL = params->GetBoxSize()/2;
	int spec_res = params->GetSpecRes();
	double *tau = new double[spec_res];
	double *x = new double[spec_res];
	double *sigma = new double[spec_res];

	//Loop through galaxies and sightlines
	for (int galn = firstgal; galn < lastgal; galn++)
	{
		if (galn > 0 && galn % 10 == 0 && firstgal == first_in_chunk) //Only print status for the first thread
			cout << "Galaxy #" << galn << " of " << lastgal << endl;
		//Initialize galaxy
		Galaxy gal = params->GetGalaxy(galn);

		for (int losn = 0; losn < params->GetNLOS(); losn++)
		{
#ifdef _OUTPUT_ALL_THE_THINGS_
			string filename;
		   	stringstream out;
			out <<	"nhi_vrad_g" << galn << "_los" << losn << ".txt";
			filename = out.str();
			cout << "Writing to " << filename << endl;
			all_stream.open(filename.c_str());
#endif

			int losn_tau = (galn-first_in_chunk)*params->GetNLOS()+losn;
			tau_out[losn_tau] = new float[spec_res];

			//Initialize photon
			double d = 0.0;
			Vector3d los = params->GetLOS(losn);
			Vector3d phot_pos = gal.pos + los*gal.r_vir*params->GetFRvir(); //Current position of the photon
			InitFreq(los, x, phot_pos, gal.V_sys);
			Sigma(x, sigma, phot_pos);
			//Init tau
			for (int i = 0; i < spec_res; i++)
				tau[i] = 0.0;
			
			//Move photon through IGM until lower wavelength is in resonance
			while (d < d_tot)
			{
				//Move photon
				Vector3d new_pos = phot_pos + dd*los;
				d += dd;
				double delta_d = 0.0;
				int move = -1;
				if (new_pos.x > boxL) {delta_d = (new_pos.x-boxL); new_pos.x = boxL; move = 0;}
				if (new_pos.x < -boxL) {delta_d = (-boxL-new_pos.x); new_pos.x = -boxL; move = 1;}
				if (new_pos.y > boxL) {delta_d = (new_pos.y-boxL); new_pos.y = boxL; move = 2;}
				if (new_pos.y < -boxL) {delta_d = (-boxL-new_pos.y); new_pos.y = -boxL; move = 3;}
				if (new_pos.z > boxL) { delta_d = (new_pos.z-boxL); new_pos.z = boxL; move = 4; }
				if (new_pos.z < -boxL) {delta_d = (-boxL-new_pos.z); new_pos.z = -boxL; move = 5;}
				d -= delta_d; //We stopped the photon, so it didn't move the whole dd
				
				//Accumulate tau
				double n_HI = params->Getn_HIAtPos(phot_pos);
				//cout << "tau ";
				for (int i = 0; i < spec_res; i++)
				{
					tau[i] += (dd-delta_d)*cst::kpc*n_HI*sigma[i];				
					//assert(tau[i] >= 0);
				}
				//cout << endl;
				
				//Output stuff
#ifdef _OUTPUT_ALL_THE_THINGS_
				float tau_sum = 0.;
				for (int i = 0; i < spec_res; i++)
					tau_sum += tau[i];

				all_stream << n_HI << " " << params->GetRadialVelAtPos(phot_pos, los) << " " << tau_sum << " " << d << endl;
#endif

				//Transform and move to new position
				LorentzTransform(x, los, phot_pos, new_pos);
				phot_pos = new_pos;
				Sigma(x, sigma, phot_pos);

				//Photon reached the edge, transport it to other side
				if (move >= 0)
				{
					if (move == 0) phot_pos.x = -boxL;
					if (move == 1) phot_pos.x = boxL;
					if (move == 2) phot_pos.y = -boxL;
					if (move == 3) phot_pos.y = boxL;
					if (move == 4) phot_pos.z = -boxL;
					if (move == 5) phot_pos.z = boxL;
					Sigma(x, sigma, phot_pos);
				}
			}
			for (int i = 0; i < spec_res; i++)
				tau_out[losn_tau][i] = tau[i];
				//tau_out[(galn-firstgal)*params->GetNLOS()+losn][i] = tau[i];

#ifdef _OUTPUT_ALL_THE_THINGS_
			all_stream.close();
#endif
		}
	}

	delete[] tau;
	delete[] x;
	delete[] sigma;
}
//------------------------------------------------------

//Initialize systemic frequency
void Simulation::InitFreq(Vector3d nhat, double *x, Vector3d pos, Vector3d V_sys)
{
	int spec_res = params->GetSpecRes();
	double dlambda = (params->GetBWUpper() - params->GetBWLower())/spec_res;
	Vector3d U_bulk = params->GetU_bulkAtPos(pos);
	float Dnu_D = params->GetDnu_DAtPos(pos);
	Vector3d Hubble = params->GetHz()*pos/1000.;
	Vector3d U_sys = (V_sys+Hubble)/cst::c*cst::nu_0/Dnu_D;
	Vector3d U_rel = U_bulk-U_sys;

	double x_shift = nhat.Dot(U_rel);

	for (int i = 0; i < spec_res; i++)
	{
		double lambda = params->GetBWLower() + (i+0.5)*dlambda;
		double nu = cst::c/(lambda * 1.e-8);
		double x_sys = (nu - cst::nu_0) /Dnu_D;
		x[i] = x_sys + x_shift;
	}
}
//------------------------------------------------------

//Lyman alpha cross section for x at pos 
void Simulation::Sigma(double *x, double *sigma_x, Vector3d pos)
{
	float Dnu_D = params->GetDnu_DAtPos(pos);
	int spec_res = params->GetSpecRes();
	double a = cst::Dnu_L/(2.*Dnu_D);
	double q;//double *q = new double[spec_res];

	for (int i = 0; i < spec_res; i++)
	{
		double x2 = x[i]*x[i];
		double z = (x2 - 0.855)/(x2 + 3.42);
		if (z <= 0.0)
			q/*[i]*/ = 0.0;
		else
			q/*[i]*/ = z*(1.+21./x2)*a/(cst::pi*(x2+1.0))
				* (0.1117 + z*(4.421 + z*(-9.207 + 5.674*z)));
		double Voigt = sqrt(cst::pi)*q/*[i]*/ + exp(-x2);
		sigma_x[i] = cst::f_12 * sqrt(cst::pi) * cst::e*cst::e/(cst::m_e*cst::c*Dnu_D)*Voigt;
	}
	
	//delete[] q;
}


//------------------------------------------------------

void Simulation::LorentzTransform(double *x, Vector3d nhat, Vector3d oldPos, Vector3d newPos)
{
	double oldD = params->GetDnu_DAtPos(oldPos);
	double newD = params->GetDnu_DAtPos(newPos);
	Vector3d oldU = params->GetU_bulkAtPos(oldPos);
	Vector3d newU = params->GetU_bulkAtPos(newPos);

	double u1n = oldU.Dot(nhat);
	double u2n = newU.Dot(nhat);

	for (int i = 0; i < params->GetSpecRes(); i++)
		x[i] = (x[i] + u1n) * oldD/newD - u2n;
}
//------------------------------------------------------

//Save the tau data array to file, in a format that matches IGMTransfer
void Simulation::WriteData(string filename, int ngals)
{
	ofstream fout(filename.c_str(), ios::out | ios::binary | ios::app);
	assert(fout);
	cout << "Writing data to " << filename << endl;
	//for (int i = startgal*params->GetNLOS(); i < stopgal*params->GetNLOS(); i++)
	for (int i = 0; i < ngals*params->GetNLOS(); i++)
	{
		fout.write((char*)tau_out[i], sizeof(float)*params->GetSpecRes());
		if (fout.bad() )
			throw  "WARNING: write failed!" ;
	}
	cout << "Done writing " << ngals*params->GetNLOS()*params->GetSpecRes() << " values." << endl;
	fout.close();
}

//------------------------------------------------------

//Write the header to the data file
void Simulation::WriteDataHeader(string filename)
{
	int n_rec = 1;
	int n_los = params->GetNLOS()*params->GetGalaxyCount();
	int dummy = 2*sizeof(int);
	cout << "Writing data header to " << filename << endl;

	ofstream fout(filename.c_str(), ios::out | ios::binary);
	assert(fout);
	fout.write((char*)&dummy, sizeof(int));
	fout.write((char*)&n_rec, sizeof(int));
	fout.write((char*)&n_los, sizeof(int));
	fout.write((char*)&dummy, sizeof(int));
	dummy = params->GetGalaxyCount()*params->GetNLOS()*params->GetSpecRes()*sizeof(float);
	fout.write((char*)&dummy, sizeof(int));
	fout.close();
}
//------------------------------------------------------

//Write the end of the data file
void Simulation::WriteDataEnd(string filename)
{
	cout << "Writing file end to " << filename << endl;
	ofstream fout(filename.c_str(), ios::out | ios::binary | ios::app);
	assert(fout);
	int dummy = params->GetGalaxyCount()*params->GetNLOS()*params->GetSpecRes()*sizeof(float);
	fout.write((char*)&dummy, sizeof(int));
	fout.close();

}
//------------------------------------------------------
//------------------------------------------------------
//------------------------------------------------------
//------------------------------------------------------


//Proxy function to start thread, because pthread doesn't really support C++ classes
void *start_thread(void *data)
{
	ThreadData *d= static_cast<ThreadData*>(data);
	d->sim->RunSimPart(d->firstgal, d->lastgal, d->first_in_chunk);
}
//------------------------------------------------------
