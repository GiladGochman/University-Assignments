#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
	int debug = 0;
	int encode = 0;
	char *key = "";
	FILE *infile = stdin;
	FILE *outfile = stdout;
	for (int i = 1; i < argc; i++)
	{
		if(debug) fprintf(stderr,"%s\n", argv[i]);
		if (strncmp(argv[i], "-D", 2) == 0)
			debug = 0;
		else if (strncmp(argv[i], "+D", 2) == 0)
			debug = 1;
		else if (strncmp(argv[i], "+e", 2) == 0)
		{
			encode = 1;
			key = argv[i] + 2;
		}
		else if (strncmp(argv[i], "-e", 2) == 0)
		{
			encode = -1;
			key = argv[i] + 2;
		}
		else if (strncmp(argv[i], "-I", 2) == 0)
		{
			infile = fopen(argv[i] + 2, "r+");
			// start code from chatgpt
			if (infile == NULL)
			{
				fprintf(stderr, "Error: Cannot open input file %s\n", argv[i] + 2);
				return 1;
			}
			// end code from chatgpt
		}
		else if (strncmp(argv[i], "-O", 2) == 0)
		{
			outfile = fopen(argv[i] + 2, "w+");
			// start code from chatgpt
			if (outfile == NULL)
			{
				fprintf(stderr, "Error: Cannot open input file %s\n", argv[i] + 2);
				return 1;
			}
			// end code from chatgpt
		}
	}
	int c = fgetc(infile);
	int keylen = strlen(key);
	int i = 0;
	while (!feof(infile))
	{
		if (c <= 'z' && c >= 'a')
		{
			c += encode * (key[i % keylen] - '0') - 'a';
			c %= 26;
			c += 'a';
		}
		if (c <= 'Z' && c >= 'A')
		{
			c += encode * (key[i % keylen] - '0') - 'A';
			c %= 26;
			c += 'A';
		}
		if (c <= '9' && c >= '0')
		{
			c += encode * (key[i % keylen] - '0') - '0';
			c %= 10;
			c += '0';
		}

		i++;
		fputc(c, outfile);

		c = fgetc(infile);
	}

	return 0;
}
