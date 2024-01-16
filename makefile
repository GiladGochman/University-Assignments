all: clean compile link

clean:
	rm ./bin/*

compile:
	# g++ -c -o ./bin/laadin.o ./src/*.cpp

link: 
	# g++ -o ./linked.o ./bin/*.o 