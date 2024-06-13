#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct virus
{
    unsigned short SigSize;
    char virusName[16];
    unsigned char *sig;
} virus;

typedef struct link
{
    struct link *nextVirus;
    virus *vir;
} link;

typedef struct fun_desc
{
    char *name;
    char (*fun)(char);
};

char *signatureFileName = "signatures-L";
int isLittleEndian;

void SetSigFileName();
void loadSig();
void detectViruses();
void fixFile();
void quit();

virus *readVirus(FILE *);
void printVirus(virus *virus);
void list_print(link *virus_list, FILE *);
link *list_append(link *virus_list, virus *data);
void list_free(link *virus_list);
void littleEndify(unsigned short *value);
char *map(char *array, int array_length, char (*f)(char))
{
    char *mapped_array = (char *)(malloc(array_length * sizeof(char)));
    for (size_t i = 0; i < array_length; i++)
    {
        mapped_array[i] = f(*(array + i));
    }

    return mapped_array;
}
int main(int argc, char **argv)
{
    char carray[5];
    struct fun_desc menu[] = {{"Set signatures file name", &SetSigFileName}, {"Load signatures", &loadSig}, {"Print signatures", &list_print}, {"Detect viruses", &detectViruses}, {"Fix file", &fixFile}, {"Quit", &quit}, {NULL, NULL}};
    int count = 0;
    for (int i = 0; menu[i].name != NULL; i++)
    {
        printf("%d. %s\n", i, menu[i].name);
        count++;
    }

    while (!feof(stdin))
    {
        int input;
        printf("Select operation from the following menu:\n");
        scanf("%d", &input);
        if (input >= 0 && input < count)
        {
            printf("Within bounds\n");
            clear_stdin();
            char *tempArray = map(carray, 6, menu[input].fun);
            strcpy(carray, tempArray);
            free(tempArray);
        }
        else
        {
            printf("Not within bounds\n");
        }
    }

    FILE *signatureFile = fopen(signatureFileName, "r");
    if (!signatureFile)
    {
        perror("Failed to open file");
        return 1;
    }

    char endian[5] = {0};
    fread(endian, 4, 1, signatureFile);
    if (strncmp(endian, "VIRB", 4) == 0)
        isLittleEndian = 0;
    else if (strncmp(endian, "VIRL", 4) == 0)
        isLittleEndian = 1;
    else
    {
        fprintf(stderr, "Unknown file format\n");
        fclose(signatureFile);
        return 1;
    }

    virus *vir;
    link *head = NULL;
    while ((vir = readVirus(signatureFile)) != NULL)
    {
        head = list_append(head, vir);
    }

    if (head)
    {
        list_print(head, stdout);
        list_free(head);
    }

    fclose(signatureFile);
    return 0;
}
void loadSig() {}
void detectViruses() {}
void fixFile()
{
    printf("not implemented!");
}
void quit()
{
    exit(0);
}

void list_print(link *virus_list, FILE *f)
{
    link *current = virus_list;
    while (current != NULL)
    {
        printVirus(current->vir);
        current = current->nextVirus;
    }
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

    if (fread(&v->SigSize, sizeof(v->SigSize), 1, file) != 1)
    {
        free(v);
        return NULL;
    }

    if (!isLittleEndian)
    {
        littleEndify(&v->SigSize);
    }

    if (fread(v->virusName, sizeof(v->virusName), 1, file) != 1)
    {
        free(v);
        return NULL;
    }

    v->sig = malloc(v->SigSize);
    if (!v->sig)
    {
        perror("Failed to allocate memory for signature");
        free(v);
        return NULL;
    }

    if (fread(v->sig, v->SigSize, 1, file) != 1)
    {
        free(v->sig);
        free(v);
        return NULL;
    }

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
    printf("\n");
}

link *list_append(link *virus_list, virus *data)
{
    link *newNode = malloc(sizeof(link));
    if (!newNode)
    {
        perror("Failed to allocate memory for link");
        return virus_list;
    }

    newNode->vir = data;
    newNode->nextVirus = NULL;

    if (!virus_list)
    {
        return newNode;
    }

    link *current = virus_list;
    while (current->nextVirus != NULL)
    {
        current = current->nextVirus;
    }
    current->nextVirus = newNode;

    return virus_list;
}

void list_free(link *virus_list)
{
    while (virus_list != NULL)
    {
        link *next = virus_list->nextVirus;
        free(virus_list->vir->sig);
        free(virus_list->vir);
        free(virus_list);
        virus_list = next;
    }
}
