#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct virus
{
    unsigned short SigSize;
    char virusName[16];
    unsigned char *sig;
} virus;

char *signatureFileName = "signatures-L";
int isLittleEndian;

virus *readVirus(FILE *file);
void littleEndify(unsigned short *value);
void printVirus(virus *v);

int main(int argc, char **argv)
{
    FILE *signatureFile = fopen(signatureFileName, "r+");
    if (!signatureFile)
    {
        perror("Failed to open file");
        return 1;
    }

    char endian[5] = {0};               // Ensure it's zero-initialized
    fread(endian, 4, 1, signatureFile); // Read the endian indicator
    if (strncmp(endian, "VIRB", 4) == 0)
        isLittleEndian = 0;
    else if (strncmp(endian, "VIRL", 4) == 0)
        isLittleEndian = 1;
    else
    {
        fprintf(stderr, "Unknown file format\n");
        return 1;
    }

    virus *vir = readVirus(signatureFile);
    if (vir != NULL)
    {
        printVirus(vir);
        free(vir->sig); // Free the allocated memory for the signature
        free(vir);      // Free the allocated memory for the virus struct
    }

    fclose(signatureFile);
    return 0;
}

void SetSigFileName()
{
    printf("Enter new signature file name: ");
    scanf("%255s", signatureFileName);
}

virus *readVirus(FILE *file)
{
    virus *v = malloc(sizeof(virus));
    if (!v)
    {
        perror("Failed to allocate memory");
        return NULL;
    }

    fread(&v->SigSize, 2, 1, file);
    if (isLittleEndian == 0)
    {
        littleEndify(&v->SigSize);
    }

    fread(v->virusName, 16, 1, file);
    // Make sure the virus name is null-terminated
    v->virusName[15] = '\0';

    v->sig = malloc(v->SigSize);
    if (!v->sig)
    {
        perror("Failed to allocate memory for signature");
        free(v);
        return NULL;
    }

    fread(v->sig, v->SigSize, 1, file);

    return v;
}

void littleEndify(unsigned short *value)
{
    *value = (*value >> 8) | (*value << 8);
}

void printVirus(virus *v)
{
    printf("Virus name: %s\n", v->virusName);
    printf("Virus sig length: %d\n", v->SigSize);
    printf("Virus signature: ");
    for (int i = 0; i < v->SigSize; i++)
    {
        printf("%02X ", v->sig[i]);
    }
    printf("\n");
}
