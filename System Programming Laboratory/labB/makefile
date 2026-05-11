all: clean compile link

clean:
	rm -f *.o AntiVirus

compile:
	gcc -g -m32 -Wall -c -o AntiVirus.o AntiVirus.c

link:
	gcc -g -m32 -Wall -o AntiVirus AntiVirus.o

