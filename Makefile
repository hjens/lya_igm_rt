all:
	cd SimpleTransfer; make
	cd MakeCelldata; make
clean:
	cd SimpleTransfer; make clean
	cd MakeCelldata; make clean
