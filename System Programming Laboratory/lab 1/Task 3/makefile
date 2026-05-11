all: clean compile link

clean:
	rm -f *.o menu_map

compile:
	gcc -g -m32 -Wall -c -o menu_map.o menu_map.c

link:
	gcc -g -m32 -Wall -o menu_map menu_map.o

