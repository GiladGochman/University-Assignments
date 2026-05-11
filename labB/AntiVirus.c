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
    void (*fun)();
} fun_desc;

char signatureFileName[256] = "signatures-L";
char suspectedFileName[256];
int isLittleEndian;

void SetSigFileName();
void loadSig();
void detectViruses();
void fixFile();
void quit();

virus *readVirus(FILE *);
int virusLocation = -1;
link *head = NULL;
void printVirus(virus *virus);
void list_print(link *virus_list, FILE *);
link *list_append(link *virus_list, virus *data);
void list_free(link *virus_list);
void littleEndify(unsigned short *value);
void clear_stdin();
void detect_virus(char *buffer, unsigned int size, link *virus_list);
void neutralize_virus(const char *filename, unsigned int offset);

void detect_virus(char *buffer, unsigned int size, link *virus_list)
{
    for (unsigned int i = 0; i < size; i++)
    {
        link *current = virus_list;
        while (current != NULL)
        {
            virus *v = current->vir;
            if (i + v->SigSize <= size)
            {
                if (memcmp(buffer + i, v->sig, v->SigSize) == 0)
                {
                    printf("Virus detected!\n");
                    printf("Starting byte: %d\n", i);
                    printf("Virus name: %s\n", v->virusName);
                    printf("Signature size: %d\n", v->SigSize);
                    virusLocation = i;
                }
            }
            current = current->nextVirus;
        }
    }
}

void neutralize_virus(const char *filename, unsigned int offset)
{
    FILE *file = fopen(filename, "r+b");
    if (!file)
    {
        perror("Failed to open file");
        return;
    }

    if (fseek(file, offset, SEEK_SET) != 0)
    {
        perror("Failed to seek to offset");
        fclose(file);
        return;
    }

    unsigned char ret_instruction = 0xC3; // RET (near) instruction
    if (fwrite(&ret_instruction, sizeof(unsigned char), 1, file) != 1)
    {
        perror("Failed to write byte");
    }
    else
    {
        printf("Successfully wrote RET instruction at offset %u\n", offset);
    }

    fclose(file);
}

int main(int argc, char **argv)
{
    if (argc >= 2)
    {
        strncpy(suspectedFileName, argv[1], sizeof(suspectedFileName) - 1);
        suspectedFileName[sizeof(suspectedFileName) - 1] = '\0';
    }

    fun_desc menu[] = {
        {"Set signatures file name", SetSigFileName},
        {"Load signatures", loadSig},
        {"Print signatures", (void (*)(void))list_print},
        {"Detect viruses", detectViruses},
        {"Fix file", fixFile},
        {"Quit", quit},
        {NULL, NULL}};

    int count = 0;
    for (int i = 0; menu[i].name != NULL; i++)
    {
        printf("%d. %s\n", i, menu[i].name);
        count++;
    }

    while (1)
    {
        int input;
        printf("Select operation from the following menu:\n");
        scanf("%d", &input);
        if (input >= 0 && input < count)
        {
            printf("Within bounds\n");
            clear_stdin();
            if (input == 2)
            {
                if (!head)
                {
                    printf("No signatures loaded\n");
                    continue;
                }
                list_print(head, stdout);
            }
            else
            {
                menu[input].fun();
            }
        }
        else
        {
            printf("Not within bounds\n");
        }
    }

    return 0;
}

void clear_stdin()
{
    int c;
    while ((c = getchar()) != '\n' && c != EOF)
        ;
}

void loadSig()
{
    FILE *signatureFile = fopen(signatureFileName, "r");
    if (!signatureFile)
    {
        perror("Failed to open file");
        return;
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
        return;
    }

    virus *vir;
    head = NULL;
    while ((vir = readVirus(signatureFile)) != NULL)
    {
        head = list_append(head, vir);
    }

    fclose(signatureFile);
}

void detectViruses()
{
    unsigned char buffer[10000];
    FILE *patient = fopen(suspectedFileName, "r+");
    if (!patient)
    {
        perror("Failed to open file");
        return;
    }

    int size = fread(buffer, 1, sizeof(buffer), patient);
    detect_virus((char *)buffer, size, head);
    fclose(patient);
}

void fixFile()
{
    FILE *patient = fopen(suspectedFileName, "r+");
    if (!patient)
    {
        perror("Failed to open file");
        return;
    }

    unsigned char buffer[10000];
    int size = fread(buffer, 1, sizeof(buffer), patient);
    if (size <= 0)
    {
        perror("Failed to read file");
        fclose(patient);
        return;
    }
    if (virusLocation != -1)
    {
        neutralize_virus(suspectedFileName, virusLocation); // Neutralize the first detected virus
    }
    else
    {
        printf("No virus location found. Try running 'Detect viruses' (option number 3) first.")
    }

    fclose(patient);
}

void quit()
{
    printf("Quit\n");
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
    clear_stdin();
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
    printf("\n\n");
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
