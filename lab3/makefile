all: clean run

start.o: start.s
	nasm -f elf32 start.s -o start.o

# main.o: main.c
	# gcc -m32 -Wall -ansi -c -nostdlib -fno-stack-protector main.c -o main.o

util.o: util.c
	gcc -m32 -Wall -ansi -c -nostdlib -fno-stack-protector util.c -o util.o

run: util.o start.o #main.o
	# ld -m elf_i386 start.o main.o util.o -o task1
	ld -m elf_i386 start.o util.o -o task1

.PHONY: clean 

clean:
	rm -f *.o
