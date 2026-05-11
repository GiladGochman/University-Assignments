all: clean myshell

myshell: myshell.o LineParser.o Looper
	gcc -g -m32 -Wall -o myshell myshell.o LineParser.o 

myshell.o: myshell.c
	gcc -m32 -g -Wall -c -o myshell.o myshell.c 

LineParser.o: LineParser.c LineParser.h
	gcc -m32 -g -Wall -c -o LineParser.o LineParser.c 

Looper: Looper.c
	gcc -m32 -g -Wall -o Looper Looper.c 

.PHONY: clean 

clean:
	rm -f *.o	
