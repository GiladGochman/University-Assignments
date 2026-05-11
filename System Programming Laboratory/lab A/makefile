all: clean compile link

clean:
	rm -f *.o encoder

compile:
	gcc -g -m32 -Wall -c -o encoder.o encoder.c

link:
	gcc -g -m32 -Wall -o encoder encoder.o

