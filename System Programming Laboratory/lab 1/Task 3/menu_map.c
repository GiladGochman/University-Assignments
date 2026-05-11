#include <stdlib.h>
#include <stdio.h>
#include <string.h>

char my_get(char c)
{
  return fgetc(stdin);
}
/* Ignores c, reads and returns a character from stdin using fgetc. */

char cprt(char c)
{
  if (c<=0x7E && c>=0x20)
  {
    // printf("%c", c);
    fputc(c,stdout);
  }
  else
  {
    // printf('.');
        fputc('.',stdout);

  }
      fputc('\n',stdout);

  return c;
}
/* If c is a number between 0x20 and 0x7E, cprt prints the character of ASCII value c followed by a new line. Otherwise, cprt prints the dot ('.') character. After printing, cprt returns the value of c unchanged. */

char encrypt(char c)
{
  if (c<=0x4E && c>=0x20)
  {
    c += 0x20;
  }
  return c;
}
/* Gets a char c. If c is between 0x20 and 0x4E add 0x20 to its value and return it. Otherwise return c unchanged */

char decrypt(char c)
{
  if (c<=0x7E && c>=0x40)
  {
    c -= 0x20;
  }
  return c;
}
/* Gets a char c and returns its decrypted form subtractng 0x20 from its value. But if c was not between 0x40 and 0x7E it is returned unchanged */

char xoprt(char c)
{
  printf("%x %o\n", c, c);
  return c;
}
char *map(char *array, int array_length, char (*f)(char))
{
  char *mapped_array = (char *)(malloc(array_length * sizeof(char)));
  /* TODO: Complete during task 2.a */
  for (size_t i = 0; i < array_length; i++)
  {
    mapped_array[i] = f(*(array + i));
  }

  return mapped_array;
}

void clear_stdin() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

int main(int argc, char **argv)
{
  char carray[5];
  struct fun_desc
  {
    char *name;
    char (*fun)(char);
  };
  struct fun_desc menu[] = {{"my_get", &my_get}, {"cprt", &cprt}, {"encrypt", &encrypt}, {"decrypt", &decrypt}, {"xoprt", &xoprt}, {NULL, NULL}};
  int count = 0;
  for (int i = 0; menu[i].name != NULL; i++)
  {
    printf("%d. %s\n", i + 1, menu[i].name);
    count++;
  }

  while (!feof(stdin))
  {
    int input;
    printf("Select operation from the following menu:\n");
    scanf("%d", &input);
    // printf("hi %s\n",input);
    if (input >= 1 && input <= count)
    {
      printf("Within bounds\n");
   clear_stdin();
      
      char *tempArray = map(carray, 5, menu[input - 1].fun);
      strcpy(carray,tempArray);
      free(tempArray);
    }
    else
    {
      printf("Not within bounds\n");
    }
  }
  return 0;
}

/* xoprt prints the value of c in a hexadecimal representation, then in octal representation, followed by a new line, and returns c unchanged. */
