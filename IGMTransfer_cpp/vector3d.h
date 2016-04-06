#ifndef VECTOR3D_H
#define VECTOR3D_H
#include <cmath>
#include <iostream>
#include <fstream>
using namespace std;

//Index a one dimensional array as if it's 3D
#define idx(M,x,y,z,l) (M[x*l*l+y*l+z])

class Vector3d
{
	public:
		Vector3d(double _x, double _y, double _z)
		{
			x = _x; y = _y; z = _z;
		}
		Vector3d()
		{
			x = y = z = 0.0;
		}
		~Vector3d(){}; //Nothing to destroy
		//---
		double Magnitude() 
		{
			return sqrt(x*x+y*y+z*z);
		}
		//Multiply by constant
		Vector3d operator*(float num) const
		{
			return Vector3d(x * num, y * num, z * num);
		}
		//Divide by constant
		Vector3d operator/(float num) const
		{
			return Vector3d(x / num, y / num, z / num);
		}
		//constant*vector
		friend Vector3d operator*(float num, Vector3d const &vec)
		{
			return Vector3d(vec.x * num, vec.y * num, vec.z * num);
		}
		//
		Vector3d & operator+=(const Vector3d &vec)
		{
			x += vec.x; y += vec.y; z += vec.z;
			return *this;
		}
		//
		Vector3d & operator-=(const Vector3d &vec)
		{
			x -= vec.x; y -= vec.y; z -= vec.z;
			return *this;
		}
		//
		Vector3d & operator*=(const Vector3d &vec)
		{
			x *= vec.x; y *= vec.y; z *= vec.z;
			return *this;
		}
		//
		Vector3d & operator/=(const Vector3d &vec)
		{
			x /= vec.x; y /= vec.y; z /= vec.z;
			return *this;
		}
		//add two vectors
		Vector3d operator+(const Vector3d &vec) const
		{
			return Vector3d(x + vec.x, y + vec.y, z + vec.z);
		}
		//add vector and double
		Vector3d operator+(const double a) const
		{
			return Vector3d(x + a, y + a, z + a);
		}

		//subtract two vectors
		Vector3d operator-(const Vector3d &vec) const
		{
			return Vector3d(x - vec.x, y - vec.y, z - vec.z);
		}

		//normalize this vector
		void Normalize()
		{
			double magnitude = this->Magnitude();
			x /= magnitude;
			y /= magnitude;
			z /= magnitude;
		}
		
		//dot product
		float Dot(const Vector3d &vec) const
		{
			return x * vec.x + y * vec.y + z * vec.z;
		}

		//cross product
		Vector3d Cross(const Vector3d &vec) const
		{
			return Vector3d(y * vec.z - z * vec.y,
					z * vec.x - x * vec.z,
					x * vec.y - y * vec.x);
		}

		//Variables
		double x, y, z;
};

ostream &operator<<(ostream &stream, Vector3d vec);
#endif
