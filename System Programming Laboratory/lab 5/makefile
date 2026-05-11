all: lab5
lab5:
	gcc -m32 -c my_loader.c -o my_loader.o
	nasm -f elf32 -o start.o start.s
	ld -o my_loader startup.o my_loader.o start.o -L/usr/lib32 -lc -T linking_script -dynamic-linker /lib32/ld-linux.so.2

clean:
	rm -f my_loader start.o my_loader.o