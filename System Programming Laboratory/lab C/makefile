all: clean mypipeline

mypipeline: mypipeline.o 
	gcc -g -m32 -Wall -o mypipeline mypipeline.o 

mypipeline.o: mypipeline.c
	gcc -m32 -g -Wall -c -o mypipeline.o mypipeline.c 

.PHONY: clean 

clean:
	rm -f *.o	