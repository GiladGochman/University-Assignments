CXX = g++

CXXFLAGS = -g -Wall -Weffc++ -std=c++11 -Iinclude

all: clean compile link 

clean:
	rm -f ./bin/*

compile:
	${CXX} ${CXXFLAGS} -c -o ./bin/file1.o ./src/main.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file2.o ./src/Warehouse.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file3.o ./src/Customer.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file4.o ./src/Volunteer.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file5.o ./src/Collector.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file6.o ./src/Order.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file7.o ./src/Driver.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file8.o ./src/LimitedCollector.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file9.o ./src/LimitedDriver.cpp
	${CXX} ${CXXFLAGS} -c -o ./bin/file11.o ./src/Actions.cpp

link:
	g++ -o ./bin/warehouse ./bin/*.o