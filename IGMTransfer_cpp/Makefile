EXECUTABLES= SimpleTransfer.x
OBJ_FILE= SimParams.o main.o Simulation.o vector3d.o
#OPTIONS= -D _NO_VEL_ -O3
#OPTIONS= -D _OUTPUT_ALL_THE_THINGS_ -O3
OPTIONS= -O3
SimpleTransfer.x: $(OBJ_FILE)
	g++ $(OPTIONS)  -pthread $(OBJ_FILE) -o SimpleTransfer.x
SimParams.o: SimParams.cpp
	g++ $(OPTIONS)  -c SimParams.cpp
Simulation.o: Simulation.cpp
	g++ $(OPTIONS)  -c Simulation.cpp
vector3d.o: vector3d.cpp
	g++ $(OPTIONS) -c vector3d.cpp
main.o: main.cpp
	g++ $(OPTIONS) -c main.cpp
clean:
	rm -f $(EXECUTABLES) $(OBJ_FILE)
