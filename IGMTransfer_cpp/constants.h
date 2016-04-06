#ifndef CONSTANTS_H
#define CONSTANTS_H
//Physical constants
namespace cst
{
	const double c 		= 2.99792458e10;			//Speed of light; cm/s
	const double nu_0     = 2.46607e15;  	//Lya line-center frequency; Hz
	const double Dnu_L    = 9.936e7;		//Lya natural line width; Hz
	const double pi       = 3.14159265358979;
	const double f_12     = 0.4162;          //Oscillator strength
	const double m_e      = 9.1093897e-28;   //Electron mass; g
	const double e        = 4.803206e-10;    //Electron charge; esu
	const double kpc      = 3.08567758131e21;//Kiloparsec; cm
	const double Mpc      = 3.08567758131e24; //Kiloparsec; cm
	const double T4 		= 1.0; //Temperature/10^4K
	const double thermal_w	= 12.845*sqrt(T4);
	const double lambda_0 = c / nu_0 * 1e8;  //Line center wavelength; Angstrom
#ifdef _OUTPUT_ALL_THE_THINGS_
	const int max_threads = 1;
#else
	const int max_threads = 8;
#endif
}
#endif
