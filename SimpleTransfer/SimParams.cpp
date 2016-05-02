#include <fstream>
#include "SimParams.h"
#include <iostream>
#include <sstream>

SimParams::SimParams()
{
}
SimParams::~SimParams()
{
	delete[] rho_HI;
	delete[] Dnu_D;
	delete[] U_bulk;
}
//-------------------------------------------------------------

//Read main config file
void SimParams::ReadConfigFile(string filename)
{
	string line;
	ifstream fin(filename.c_str());
	stringstream str;
	assert (fin);
	cout << "Reading config file " << filename << endl;

	getline(fin, line); str.str(line); str >> data_dir;
	getline(fin, line); str.str(line); str >> celldata_file;
	getline(fin, line); str.str(line); str >> galdata_file;
	getline(fin, line); str.str(line); str >> data_filename;
	getline(fin, line); str.str(line); str >> redshift;
	getline(fin, line); str.str(line); str >> f_rvir;
	getline(fin, line); str.str(line); str >> spec_res;
	getline(fin, line); str.str(line); str >> BW_lower >> BW_upper;
	getline(fin, line); str.str(line); str >> num_los;
	getline(fin, line); str.str(line); str >> num_los_write;
	getline(fin, line); str.str(line); str >> sim_rad;
	getline(fin, line); str.str(line); str >> H0;
	getline(fin, line); str.str(line); str >> Omega0;
	getline(fin, line); str.str(line); str >> lam;
	getline(fin, line); str.str(line); str >> los_dirs;
	fin.close();

	//Print values read
	cout << "Read config file: " << endl;
	cout << data_dir << endl;
	cout << celldata_file << endl;
	cout << galdata_file << endl;
	cout << data_filename << endl;
	cout << redshift << endl;
	cout << f_rvir << endl;
	cout << spec_res << endl;
	cout << BW_lower << BW_upper << endl;
	cout << num_los << endl;
    cout << num_los_write << endl;
	cout << sim_rad << endl;
	cout << H0 << endl;
	cout << Omega0 << endl;
	cout << lam << endl;
	cout << los_dirs << endl;
	cout << "..." << endl;

}
//-------------------------------------------------------------

//Read galaxy data and store in the linked list galaxies
void SimParams::ReadGalData()
{
	string filename = data_dir + "/" + galdata_file;
	cout << "Reading galaxy data from " << filename << "..." << endl;
	ifstream file(filename.c_str());
	string line ;
	while( getline(file, line) ) 
	{
		if (line[0] != '#') //Not a comment, read galaxy data
		{
			stringstream str(line);
			Galaxy gal;
			str >> gal.pos.x >> gal.pos.y >> gal.pos.z 
				>> gal.r_vir >> gal.V_sys.x >> gal.V_sys.y >> gal.V_sys.z >> gal.logmass;
#ifdef _NO_VEL_
			gal.V_sys = GetHz()*gal.pos*1.e-3;
#endif
			gal.V_sys = gal.V_sys*1.e5; // -> cm/s
			galaxies.push_back(gal);
		}
	}
	cout << "...done. Read " << galaxies.size() << " galaxies. " << endl;
}
//-------------------------------------------------------------

//Read CellData file, containing neutral density and gas velocities
void SimParams::ReadCellData()
{
	string filename = data_dir + "/" + celldata_file;
	cout << "Reading cell data from " << filename << endl;
	ifstream fin(filename.c_str(), ios::in | ios::binary);
	assert (fin);
	int n_cells, mesh_x, mesh_y, mesh_z, dummy;

	//Read header data
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	fin.read(reinterpret_cast<char*>(&n_cells), sizeof(n_cells));
	fin.read(reinterpret_cast<char*>(&D_box), sizeof(D_box));
	fin.read(reinterpret_cast<char*>(&mesh_x), sizeof(mesh_x));
	fin.read(reinterpret_cast<char*>(&mesh_y), sizeof(mesh_y));
	fin.read(reinterpret_cast<char*>(&mesh_z), sizeof(mesh_z));
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	assert(n_cells == mesh_x*mesh_y*mesh_z);
	assert(mesh_x == mesh_y);
	assert(mesh_y == mesh_z);
	mesh_size = mesh_x;

	cout << "Mesh size is " << mesh_size << endl;

	//Read level string -- then throw it away
	for (int i = 0; i < n_cells; i++)
	{
		fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
		assert(dummy == 0);
	}
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));

	//Read n_HI
	rho_HI = new float[n_cells];
	float rho_sum = 0;
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	for (int i = 0; i < n_cells; i++)
	{
		fin.read(reinterpret_cast<char*>(&rho_HI[i]), sizeof(rho_HI[i]));
		rho_sum += rho_HI[i];
	}
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));

	//Read Dnu_D
	Dnu_D = new float[n_cells];
	float Dnu_D_sum = 0;
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	for (int i = 0; i < n_cells; i++)
	{
		fin.read(reinterpret_cast<char*>(&Dnu_D[i]), sizeof(Dnu_D[i]));
		Dnu_D_sum += Dnu_D[i];
	}
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));

	U_bulk = new Vector3d[n_cells];
	float temp;
	//x component
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	for (int i = 0; i < n_cells; i++)
	{
		fin.read(reinterpret_cast<char*>(&temp), sizeof(temp));
		U_bulk[i].x = temp;
	}
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	//y component
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	for (int i = 0; i < n_cells; i++)
	{
		fin.read(reinterpret_cast<char*>(&temp), sizeof(temp));
		U_bulk[i].y = temp;
	}
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	//z component
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));
	for (int i = 0; i < n_cells; i++)
	{
		fin.read(reinterpret_cast<char*>(&temp), sizeof(temp));
		U_bulk[i].z = temp;
	}
	fin.read(reinterpret_cast<char*>(&dummy), sizeof(dummy));

	fin.close();

	//Remove the Hubble flow component
	RemoveHubbleFlow();


	//Print some statistics to make sure all is OK
	double mean_vel = 0.0;
	for (int i = 0; i < n_cells; i++)
		mean_vel += U_bulk[i].Magnitude();
	cout << "n_cells: " << n_cells << endl;
	cout << "D_box: " << D_box << endl;
	cout << "mesh_size: " << mesh_x << endl;
	cout << "Mean HI density: " << rho_sum/(float)n_cells << " cm^-3" << endl;
	cout << "Mean Dnu_D: " << Dnu_D_sum/(float)n_cells << endl;
	cout << "Mean abs(vel): " << mean_vel/(double)n_cells << " km/s" << endl;
}
//-------------------------------------------------------------

//Read line-of-sight vectors
//If filename is 'x', 'y' or 'z', set equal to coordinate axis
void SimParams::ReadLOSDir()
{
	string filename;
	if (los_dirs == "x" || los_dirs == "y" || los_dirs == "z")
		filename = los_dirs;
	else
	   filename	= data_dir + "/" + los_dirs;

	if (filename == "x")
	{
		LOS_dir.push_back(Vector3d(1.0, 0.0, 0.0));
		cout << "Sightlines along x-axis" << endl;
	}
	else if (filename == "y")
	{
		LOS_dir.push_back(Vector3d(0.0, 1.0, 0.0));
		cout << "Sightlines along y-axis" << endl;
	}
	else if (filename == "z")
	{
		LOS_dir.push_back(Vector3d(0.0, 0.0, 1.0));
		cout << "Sightlines along z-axis" << endl;
	}
	else //Read file
	{
		cout << "Reading sightlines from " << filename << endl;
		ifstream file(filename.c_str());
		string line;
		assert (file);
		for (int i = 0; i < num_los; i++)
		{
			getline(file,line);
			stringstream str(line);
			Vector3d LOS;
			str >> LOS.x >> LOS.y >> LOS.z;
			LOS_dir.push_back(LOS);
		}
		file.close();
	}
}
//-------------------------------------------------------------

//Find the cell att pos (given in pkpc, from the origin) and return 
//the gas velocity at that point
Vector3d SimParams::GetU_bulkAtPos(Vector3d pos)
{
	//We add the Hubble flow velocity here
	int cellx = (int)((pos.x+D_box/2)/D_box*(double)mesh_size);
	int celly = (int)((pos.y+D_box/2)/D_box*(double)mesh_size);
	int cellz = (int)((pos.z+D_box/2)/D_box*(double)mesh_size);
	Vector3d hubble = pos/1000.*GetHz();
	return idx(U_bulk, cellx, celly, cellz, mesh_size)+hubble/cst::thermal_w;
}
//-------------------------------------------------------------

//Get the velocity at pos parallel to nhat
float SimParams::GetRadialVelAtPos(Vector3d pos, Vector3d nhat)
{
	int cellx = (int)((pos.x+D_box/2)/D_box*(double)mesh_size);
	int celly = (int)((pos.y+D_box/2)/D_box*(double)mesh_size);
	int cellz = (int)((pos.z+D_box/2)/D_box*(double)mesh_size);
	Vector3d vel = idx(U_bulk, cellx,celly,cellz, mesh_size)*cst::thermal_w;
	return vel.Dot(nhat);
}
//-------------------------------------------------------------
float SimParams::GetDnu_DAtPos(Vector3d pos)
{
	int cellx = (int)((pos.x+D_box/2)/D_box*(double)mesh_size);
	int celly = (int)((pos.y+D_box/2)/D_box*(double)mesh_size);
	int cellz = (int)((pos.z+D_box/2)/D_box*(double)mesh_size);
	return idx(Dnu_D, cellx, celly, cellz, mesh_size);
}
//-------------------------------------------------------------
double SimParams::Getn_HIAtPos(Vector3d pos)
{
	int cellx = (int)((pos.x+D_box/2)/D_box*(double)mesh_size);
	int celly = (int)((pos.y+D_box/2)/D_box*(double)mesh_size);
	int cellz = (int)((pos.z+D_box/2)/D_box*(double)mesh_size);
	double n_HI = idx(rho_HI, cellx, celly, cellz, mesh_size);
	return n_HI;
}
//-------------------------------------------------------------

//Remove the Hubble flow contribution from U_bulk
//This is then added in again in GetU_bulkAtPos, calculated
//from true position, not cell
void SimParams::RemoveHubbleFlow()
{
	double Hz = GetHz();
	for (int cellx = 0; cellx < mesh_size; cellx++)
	{
		for (int celly = 0; celly < mesh_size; celly++)
		{
			for (int cellz = 0; cellz < mesh_size; cellz++)
			{
				double dx = (double)(cellx-mesh_size/2)/(double)(mesh_size)*GetBoxSize()/1000.;
				double dy = (double)(celly-mesh_size/2)/(double)(mesh_size)*GetBoxSize()/1000.;
				double dz = (double)(cellz-mesh_size/2)/(double)(mesh_size)*GetBoxSize()/1000.;
				Vector3d hubble (dx*Hz, dy*Hz, dz*Hz);
#ifdef _NO_VEL_
				idx(U_bulk, cellx, celly, cellz, mesh_size) = Vector3d(0.0, 0.0, 0.0);
#else
				idx(U_bulk, cellx, celly, cellz, mesh_size) -= hubble/cst::thermal_w;
#endif
			}
		}
	}
}
//-------------------------------------------------------------

//Get the total distance in kpc that the photon has to travel for the lower wavelength to 
//shift into resonance
float SimParams::GetDtot()
{
	double H = GetHz()*3.240779289e-20; //Hz in cm/s/cm
	return (cst::lambda_0 - GetBWLower())/GetBWLower()*cst::c/H/cst::kpc;
}
//-------------------------------------------------------------
