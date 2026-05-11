#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <errno.h>
#include <stdint.h>

typedef struct
{
    char debug_mode;
    char file_name[128];
    int unit_size;
    unsigned char mem_buf[10000];
    size_t mem_count;
    char display_flag;
    /*
   .
   .
   Any additional fields you deem necessary
  */
} state;

//Functions Declerations:
void Toggle_Debug_Mode(state *s);
void Set_File_Name(state *s);
void Set_Unit_Size(state *s);
void Quit(state *s);
void Load_Into_Memory(state *s);
void Toggle_Display_Mode(state *s);
void Memory_Display(state *s);
void Save_Into_File(state *s);
void Memory_Modify(state *s);

int main()
{

    state *s = (state *)malloc(sizeof(state));
    if (s == NULL)
    {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    s->debug_mode = 0;
    s->unit_size = 1;
    s->mem_count = 0;
    s->display_flag = 0;

    struct fun_desc
    {
        char *name;
        void (*fun)(state *);
    };

    char buffer[100];

    struct fun_desc menu[] = {
        {"Toggle Debug Mode", Toggle_Debug_Mode},
        {"Set File Name", Set_File_Name},
        {"Set Unit Size ", Set_Unit_Size},
        {"Load Into Memory", Load_Into_Memory},
        {"Toggle Display Mode ", Toggle_Display_Mode},
        {"Memory Display", Memory_Display},
        {"Save Into File ", Save_Into_File},
        {"Memory Modify ", Memory_Modify},
        {"Quit ", Quit},
        {NULL, NULL}};

    while (!feof(stdin))
    {

        if (s->debug_mode == 1)
        {
            printf("Unit Size: %d\n", s->unit_size);
            printf("File Name: %s\n", s->file_name);
            printf("Memory count: %d\n", s->mem_count);
        }

        printf("Choose action:\n");
        for (int i = 0; i < sizeof(menu) / sizeof(menu[0]) - 1; i++)
        {
            printf("%d%s %s\n", i, ") ", menu[i].name);
        }

        if (fgets(buffer, sizeof(buffer), stdin) == NULL)
        { // I read in the Internet what are the arguments of fgets
            break;
        }

        printf("Option: %s", buffer);

        int input = atoi(buffer);
        if (input >= 0 && input < sizeof(menu) / sizeof(menu[0]) - 1)
        {
            menu[input].fun(s);
        }
        else
        {
            printf("Invalid option\n");
        }
    }

    free(s);
    return 0;
}

//task0b----------------------------------------------------------------
void Toggle_Debug_Mode(state *s)
{
    if (s->debug_mode == 1)
    {
        s->debug_mode = 0;
        printf("Debug flag now off\n");
    }
    else
    {
        s->debug_mode = 1;
        printf("Debug flag now on\n");
    }
}

void Set_File_Name(state *s)
{
    printf("Enter file name: ");
    fgets(s->file_name, 101, stdin);                  // Read input from user
    s->file_name[strcspn(s->file_name, "\n")] = '\0'; // Remove newline character

    if (s->debug_mode == 1)
    {
        fprintf(stderr, "Debug: file name set to '%s'\n", s->file_name);
    }
}

void Set_Unit_Size(state *s)
{
    int input;
    printf("Enter unit size (1, 2, or 4): ");
    if (scanf("%d", &input) != 1)
    {
        fprintf(stderr, "Invalid input. Please enter a number.\n");
        return;
    }

    if (input == 1 || input == 2 || input == 4)
    {
        s->unit_size = input;
        if (s->debug_mode == 1)
        {
            fprintf(stderr, "Debug: set size to %d\n", s->unit_size);
        }
    }
    else
    {
        fprintf(stderr, "Error: Invalid size. Please enter 1, 2, or 4.\n");
    }
}

void Quit(state *s)
{
    if (s->debug_mode == 1)
    {
        fprintf(stderr, "quitting\n");
    }
    exit(0);
};

void Load_Into_Memory(state *s)
{

    // Check if file_name is empty
    if (s->file_name == NULL || strcmp(s->file_name, "") == 0)
    {
        printf("Error: File name is empty.\n");
        return;
    }

    // Open file_name for reading
    FILE *file = fopen(s->file_name, "rb");
    if (file == NULL)
    {
        printf("Error: Failed to open file '%s': %s\n", s->file_name, strerror(errno));
        return;
    }

    // Prompt the user for location in hexadecimal, and length in decimal
    printf("Please enter <location> <length>\n");
    char input[256];
    if (fgets(input, sizeof(input), stdin) == NULL)
    {
        printf("Error: Failed to read input.\n");
        fclose(file);
        return;
    }

    unsigned int location;
    int length;
    if (sscanf(input, "%x %d", &location, &length) != 2)
    {
        printf("Error: Invalid input format. Expected <location> in hexadecimal and <length> in decimal.\n");
        fclose(file);
        return;
    }

    // If debug flag is on, print the file_name, location, and length
    if (s->debug_mode == 1)
    {
        printf("Debug: file_name=%s, location=0x%X, length=%d\n", s->file_name, location, length);
    }

    // Check if location and length are within valid range
    if (location + length * s->unit_size > 10000)
    {
        printf("Error: Specified range exceeds memory buffer size.\n");
        fclose(file);
        return;
    }

    // Copy length * unit_size bytes from file_name starting at position location into mem_buf
    fseek(file, location, SEEK_SET);
    size_t bytes_read = fread(s->mem_buf, s->unit_size, length, file);
    if (bytes_read < length)
    {
        printf("Warning: Only %zu units could be read from the file.\n", bytes_read);
    }
    else
    {
        printf("Loaded %zu units into memory\n", bytes_read);
    }

    // Close the file
    fclose(file);
}

void Toggle_Display_Mode(state *s)
{
    if (s->display_flag == 1)
    {
        s->display_flag = 0;
        printf("Display flag now off, decimal representation\n");
    }
    else
    {
        s->display_flag = 1;
        printf("Display flag now on, hexadecimal representation\n");
    }
}

void Memory_Display(state *s)
{
    // Prompt the user for address in hexadecimal, and length in decimal
    printf("Enter address and length\n");
    char input[256];
    if (fgets(input, sizeof(input), stdin) == NULL)
    {
        printf("Error: Failed to read input.\n");
        return;
    }

    unsigned int addr;
    int u;
    if (sscanf(input, "%x %d", &addr, &u) != 2)
    {
        printf("Error: Invalid input format. Expected <address> in hexadecimal and <length> in decimal.\n");
        return;
    }

    // If addr is 0, start from mem_buf
    if (addr == 0)
    {
        addr = (unsigned int)(uintptr_t)s->mem_buf;
    }

    // Validate the range
    if (addr < (unsigned int)(uintptr_t)s->mem_buf || addr + u * s->unit_size > (unsigned int)(uintptr_t)(s->mem_buf + 10000))
    {
        printf("Error: Specified range exceeds memory buffer size.\n");
        return;
    }

    // Display the units
    printf(s->display_flag ? "Hexadecimal\n===========\n" : "Decimal\n=======\n");
    for (int i = 0; i < u; ++i)
    {
        unsigned int data;
        memcpy(&data, (void *)(uintptr_t)addr + i * s->unit_size, s->unit_size);

        if (s->display_flag)
        {
            printf("%X\n", data);
        }
        else
        {
            printf("%u\n", data);
        }
    }
}
void Save_Into_File(state *s)
{
    if (s->file_name == NULL)
    {
        printf("Error: No file name set. Please set the file name using option 1.\n");
        return;
    }

    uintptr_t source_address;
    uintptr_t target_location;
    size_t length;

    // Prompting user for input
    printf("Please enter <source-address> <target-location> <length>\n");
    if (scanf("%x %x %zu", &source_address, &target_location, &length) != 3)
    {
        printf("Error: Invalid input.\n");
        return;
    }

    if (source_address == 0)
    {
        source_address = (uintptr_t)s->mem_buf;
    }
    else
    {
        // Check if the source address is within the bounds of mem_buf
        if (source_address < (uintptr_t)s->mem_buf || source_address >= (uintptr_t)(s->mem_buf + sizeof(s->mem_buf)))
        {
            printf("Error: Source address is out of bounds.\n");
            return;
        }
    }

    // Calculate the end address and check bounds
    uintptr_t end_address = source_address + (length * s->unit_size);
    if (end_address > (uintptr_t)(s->mem_buf + sizeof(s->mem_buf)))
    {
        printf("Error: Source address and length exceed memory buffer size.\n");
        return;
    }

    FILE *file = fopen(s->file_name, "r+b");
    if (file == NULL)
    {
        printf("Error: Could not open file '%s'.\n", s->file_name);
        return;
    }

    // Check file size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);

    if (target_location > file_size)
    {
        printf("Error: Target location is beyond the end of the file.\n");
        fclose(file);
        return;
    }

    // Seek to target location and write data
    fseek(file, target_location, SEEK_SET);
    size_t bytes_to_write = length * s->unit_size;
    size_t bytes_written = fwrite((void *)source_address, 1, bytes_to_write, file);

    if (bytes_written != bytes_to_write)
    {
        printf("Error: Could not write all bytes to the file. Written: %zu, Expected: %zu\n", bytes_written, bytes_to_write);
    }
    else
    {
        printf("Successfully wrote %zu units to '%s' at offset 0x%x\n", length, s->file_name, target_location);
    }

    fclose(file);
}
// void Save_Into_File(state *s)
// {

//     printf("Please enter <source address> <target location> <length>\n");
//     int sourceAddr, targetAddr, len;

//     if (scanf("%x %x %d", sourceAddr, targetAddr, len) == NULL)
//     {
//         printf("Error: Failed to read input.\n");
//         //fclose(file);
//         return;
//     }
//     File *targetFile = fopen(s->file_name, "w");
//     if ()
//     {
//         /* code */
//     }
// }

void Memory_Modify(state *s)
{
    printf("not implemented yet!\n");
}
