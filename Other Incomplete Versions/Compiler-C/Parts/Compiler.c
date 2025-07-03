#include <stdio.h>
#include <stdlib.h>
#include <regex.h>
#include <string.h>
#include <ctype.h>
#include "Parts/1 Tokenizer.h"
#include "Parts/"

char *open_file(char *filename)
{
    FILE *file = fopen(filename, "r");

    if (!file)
    {
        printf("Failed to open file");
        exit(1);
    }

    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *file_contents = (char *)malloc(file_size + 1);

    if (!file_contents)
    {
        printf("Failed to allocate memory for file contents");
        fclose(file);
        exit(1);
    }

    size_t read_size = fread(file_contents, 1, file_size, file);
    file_contents[read_size] = '\0';

    fclose(file);

    // printf("File size: %ld\n", file_size);

    return file_contents;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: Compile.exe <filename>\n");
        return 1;
    }

    printf("\n");

    char *file_content = open_file(argv[1]);

    struct Token *tokens = tokenize(file_content);
    struct Token *tokens = tokenize(file_content);

    printf("\n");
}