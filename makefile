all: clean compile link

clean:
	rm -f ./bin/*

compile:
	g++ -c -o ./bin/file1.o ./src/main.cpp
	g++ -c -o ./bin/file2.o ./src/Warehouse.cpp

link:
	g++ -o ./warehouse ./bin/*.o