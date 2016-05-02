#ifndef SIMPARAMS_H
#define SIMPARAMS_H

#include "vector3d.h"
#include <string>
#include <vector> 
#include <cassert>
#include "constants.h"
using namespace std;

//A galaxy
struct Galaxy
{
	Vector3d pos;
	double r_vir;
	Vector3d V_sys;
	double logmass;
};


//Class containing parameters and input arrays for the simulation
class SimParams
{
	public:
		SimParams();
		~SimParams();
		
		//Read files
		void ReadGalData();
		void ReadCellData();
		void ReadLOSDir();
		void ReadConfigFile(string filename);

		//Get access to parameters
		Galaxy GetGalaxy(int idx) 
			{assert(idx<galaxies.size());return galaxies[idx];}
		int GetGalaxyCount() 
			{return galaxies.size();}
		int GetNLOS() {return LOS_dir.size();}
		Vector3d GetLOS(int idx) {assert(idx<LOS_dir.size()); return LOS_dir[idx];}
		float GetFRvir() {return f_rvir;}
		int GetMeshSize() {return mesh_size;} //Number of cells per side
		int GetBoxSize() {return D_box;} //pkpc
		int GetSpecRes() {return spec_res;} 
		double GetBWLower() {return BW_lower;} 
		double GetBWUpper() {return BW_upper;}
		double GetZ() {return redshift;} 
		double GetHz() {return H0*sqrt(Omega0*pow(1.0+GetZ(),3) + lam);}

		Vector3d GetU_bulkAtPos(Vector3d pos);
		float GetRadialVelAtPos(Vector3d pos, Vector3d nhat);
		float GetDnu_DAtPos(Vector3d pos);
		double Getn_HIAtPos(Vector3d pos);
		float GetDtot();

		string GetOutdataFilename() {return data_dir + "/" + data_filename;}
	private:
		void RemoveHubbleFlow();
		float *rho_HI;
		float *Dnu_D;
		double D_box;
		int mesh_size; //Assume mesh_x = mesh_y = mesh_z
		Vector3d *U_bulk;
		vector<Galaxy> galaxies;
		vector<Vector3d> LOS_dir;

		//Parameters read from config file
		string data_dir;
		string celldata_file;
		string galdata_file;
		string data_subdir_in;
		string data_filename;
		string proc_filename;
		double redshift;
		double f_rvir;
		int spec_res;
		double BW_lower, BW_upper;
		double BW_lower_stat, BW_upper_stat;
		int num_los;
		int num_los_write;
		double sim_rad; //Not used
		double H0;
		double Omega0;
		double lam;
		string los_dirs;	
};

#endif
