all: clean compile link 

clean:
	rm -f ./bin/*

compile:
	g++ -c -o ./bin/file1.o ./src/main.cpp
	g++ -c -o ./bin/file2.o ./src/Warehouse.cpp
	g++ -c -o ./bin/file3.o ./src/Customer.cpp
	g++ -c -o ./bin/file4.o ./src/Volunteer.cpp
	g++ -c -o ./bin/file5.o ./src/Collector.cpp
	g++ -c -o ./bin/file6.o ./src/Order.cpp
	g++ -c -o ./bin/file7.o ./src/Driver.cpp
	g++ -c -o ./bin/file8.o ./src/LimitedCollector.cpp
	g++ -c -o ./bin/file9.o ./src/LimitedDriver.cpp
	g++ -c -o ./bin/file10.0 ./src/BaseAction.cpp
	g++ -c -o ./bin/file11.o ./src/Actions.cpp

link:
	g++ -o ./bin/warehouse ./bin/*.o