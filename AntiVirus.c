
#include <stdio.h>

typedef struct virus
{
    unsigned short SigSize;
    char virusName[16];
    unsigned char *sig;
} virus;

char *signatureFileName = "signatures-L";
int isLittleEndian;

virus *readVirus(FILE *file);
void *bigEndify(char *bytes);

int main(int argc, char **argv)
{
    FILE *signatureFile = fopen(signatureFileName, "r+");
    char *endian;
    // Read a single 4 letter word to "endian" [VIRB/VIRL]
    fread(endian, 4, 1, signatureFileName);
    if (strncmp(endian, "VIRB") == 0)
        isLittleEndian = 0;
    else if (strncmp(endian, "VIRL") == 0)
        isLittleEndian = 1;
    else
        ;
    virus *vir = readVirus(signatureFile);
    printVirus(vir);

    // while (1)
    {
        // printf("0) Set signatures file name\n");
        // printf("1) Load signatures\n");
        // printf("2) Print signatures\n");
        // printf("3) Detect viruses\n");
        // printf("4) Fix file\n");
        // printf("5) Quit\n");
        // printf("Option: ");
    }
    return 0;
}

void SetSigFileName()
{
    printf("Enter new signature file name: ");
    scanf("%255s", "\n", signatureFileName);
}

virus *readVirus(FILE *file)
{
    virus *v;
    fread(v->SigSize, 2, 1, file);
    if (isLittleEndian)
        v->SigSize = bigEndify(v->SigSize);
    fread(v->virusName, 16, 1, file);
    if (isLittleEndian)
        strncpy(v->virusName, bigEndify(v->virusName), v->SigSize);
    // v.virusName = bigEndify(v.virusName);
    // sig is a pointer, might need to derefrence
    fread(v->sig, v->SigSize, 1, file);
    if (isLittleEndian)
        v->sig = bigEndify(v->sig);
    return v;
}

void *bigEndify(char *bytes)
{
    int n = sizeof(bytes);
    void *newBytes[n];
    for (size_t i = 0; i < n; i++)
    {
        newBytes[n - i - 1] = bytes[i];
    }
    return newBytes;
}

void printVirus(virus *v)
{
    printf("Virus name: %s \n", v->virusName);
    printf("Virus sig length: %d \n", v->SigSize);
    printf("Virus name: %p \n", v->virusName);
}

// void list_print(link *virus_list, FILE *output)
// {
// }

// link *list_append(link *virus_list, virus *data)
// {
// }

// void list_free(link *virus_list)
// {
// }

// void detect_virus(char *buffer, unsigned int size, link *virus_list)
// {
// }

// void neutralize_virus(char *fileName, int signatureOffset)
// {
// }
