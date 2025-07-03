#ifndef PARSER_H
#define PARSER_H


typedef struct Token
{
    char *type;
    char *value;
    int line;
    int character;
} Token;


Token *tokenize(char *file_content);

#endif
