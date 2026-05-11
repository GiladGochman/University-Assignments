all: clean compile link

clean:
	rm -f *.o myshell looper

compile:
	gcc -g -m32 -Wall -c -o myshell.o myshell.c
	gcc -g -m32 -Wall -c -o LineParser.o LineParser.c
	gcc -g -m32 -Wall -c -o looper.o looper.c


link:
	gcc -g -m32 -Wall -o myshell myshell.o LineParser.o
	gcc -g -m32 -Wall -o looper looper.o

