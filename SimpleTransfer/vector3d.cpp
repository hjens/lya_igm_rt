#include "vector3d.h"
ostream &operator<<(ostream &stream, Vector3d vec)
{
	stream << "(" << vec.x << ", " << vec.y << ", " << vec.z << ")";
	return stream;
}
