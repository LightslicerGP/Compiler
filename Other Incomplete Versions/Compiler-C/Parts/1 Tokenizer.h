#ifndef TOKENIZER_H
#define TOKENIZER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Token
{
    char *type;
    char *value;
    int line;
    int character;
} Token;

Token *tokenize(char *file_content);

#endif
