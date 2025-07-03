#include <stdio.h>
#include <stdlib.h>
#include <regex.h>
#include <string.h>
#include <ctype.h>

typedef enum
{
    void_type,
    int_type,
    char_type,
    struct_type,
    define,
    include,
    increment,
    decrement,
    addition_assign,
    subtraction_assign,
    multiplication_assign,
    division_assign,
    modulo_assign,
    and_compare,
    or_compare,
    ampersand,
    equal,
    less_equal,
    more_equal,
    not_equal,
    hashtag,
    left_paren,
    right_paren,
    left_brace,
    right_brace,
    left_bracket,
    right_bracket,
    less_than,
    more_than,
    colon,
    semicolon,
    question_mark,
    plus,
    minus,
    asterisk,
    forwardslash,
    percent,
    backslash,
    not,
    invert,
    float_type,
    integer,
    period,
    comma,
    string,
    identifier
} token_type;

const char *token_type_to_string(token_type type)
{
    switch (type)
    {
    case void_type:
        return "void_type";
    case int_type:
        return "int_type";
    case char_type:
        return "char_type";
    case struct_type:
        return "struct_type";
    case define:
        return "define";
    case include:
        return "include";
    case increment:
        return "increment";
    case decrement:
        return "decrement";
    case addition_assign:
        return "addition_assign";
    case subtraction_assign:
        return "subtraction_assign";
    case multiplication_assign:
        return "multiplication_assign";
    case division_assign:
        return "division_assign";
    case modulo_assign:
        return "modulo_assign";
    case and_compare:
        return "and_compare";
    case or_compare:
        return "or_compare";
    case ampersand:
        return "ampersand";
    case equal:
        return "equal";
    case less_equal:
        return "less_equal";
    case more_equal:
        return "more_equal";
    case not_equal:
        return "not_equal";
    case hashtag:
        return "hashtag";
    case left_paren:
        return "left_paren";
    case right_paren:
        return "right_paren";
    case left_brace:
        return "left_brace";
    case right_brace:
        return "right_brace";
    case left_bracket:
        return "left_bracket";
    case right_bracket:
        return "right_bracket";
    case less_than:
        return "less_than";
    case more_than:
        return "more_than";
    case colon:
        return "colon";
    case semicolon:
        return "semicolon";
    case question_mark:
        return "question_mark";
    case plus:
        return "plus";
    case minus:
        return "minus";
    case asterisk:
        return "asterisk";
    case forwardslash:
        return "forwardslash";
    case percent:
        return "percent";
    case backslash:
        return "backslash";
    case not:
        return "not";
    case invert:
        return "invert";
    case float_type:
        return "float_type";
    case integer:
        return "integer";
    case period:
        return "period";
    case comma:
        return "comma";
    case string:
        return "string";
    case identifier:
        return "identifier";
    default:
        return "unknown";
    }
}

struct Token
{
    token_type type;
    char *value;
    int line;
    int character;
};

struct RegexRule
{
    char *pattern;
    token_type token_name;
};

struct RegexRule regex_rules[] = {
    {"\\bvoid\\b", void_type},
    {"\\bint\\b", int_type},
    {"\\bchar\\b", char_type},
    {"\\bstruct\\b", struct_type},
    {"\\bdefine\\b", define},
    {"\\binclude\\b", include},
    {"\\+\\+", increment},
    {"--", decrement},
    {"\\+=", addition_assign},
    {"-=", subtraction_assign},
    {"\\*=", multiplication_assign},
    {"/=", division_assign},
    {"%=", modulo_assign},
    {"&&", and_compare},
    {"\\|\\|", or_compare},
    {"==", equal},
    {"<=", less_equal},
    {">=", more_equal},
    {"!=", not_equal},
    {"#", hashtag},
    {"\\(", left_paren},
    {"\\)", right_paren},
    {"\\{", left_brace},
    {"\\}", right_brace},
    {"\\[", left_bracket},
    {"\\]", right_bracket},
    {"<", less_than},
    {">", more_than},
    {":", colon},
    {";", semicolon},
    {"\\?", question_mark},
    {"\\+", plus},
    {"-", minus},
    {"\\*", asterisk},
    {"/", forwardslash},
    {"%", percent},
    {"&", ampersand},
    {"=", equal},
    {"\\\\", backslash},
    {"!", not},
    {"~", invert},
    {"^-?\\d*\\.\\d+", float_type},
    {"^-?\\d+", integer},
    {"\\.", period},
    {",", comma},
    {"(?:'(?:[^'\\\\]|\\\\.)*'|\"(?:[^\"\\\\]|\\\\.)*\")", string}};

const int regex_rule_count = sizeof(regex_rules) / sizeof(regex_rules[0]);

int is_line_blank(const char *line)
{
    for (int i = 0; line[i] != '\0'; i++)
    {
        if (line[i] != ' ' && line[i] != '\t' && line[i] != '\r' && line[i] != '\n')
        {
            return 0;
        }
    }
    return 1;
}

struct Token *tokens = NULL;
int tokens_capacity = 0;
int tokens_count = 0;

void add_token(token_type type, const char *value, int line, int character)
{
    if (tokens_count >= tokens_capacity)
    {
        tokens_capacity = tokens_capacity == 0 ? 8 : tokens_capacity * 2;
        tokens = realloc(tokens, tokens_capacity * sizeof(struct Token));
        if (!tokens)
        {
            fprintf(stderr, "Memory allocation failed for tokens\n");
            exit(1);
        }
    }

    tokens[tokens_count].type = type;
    tokens[tokens_count].value = strdup(value); // make a copy
    tokens[tokens_count].line = line;
    tokens[tokens_count].character = character;
    tokens_count++;
}

#define MAX_MATCH 1

char *tokenize(char *file_content)
{

    int line_offset = 0;
    int current_char;
    char *line = NULL;
    int line_length;
    int line_num = 1; // start at 1
    // int is_first_token = 1;
    size_t rule_count = sizeof(regex_rules) / sizeof(regex_rules[0]);

    while (file_content[line_offset] != '\0')
    {
        int current_char = 0;
        char *line = NULL;
        int line_length = 0;

        while (file_content[line_offset + current_char] != '\n' &&
               file_content[line_offset + current_char] != '\0')
        {
            line = realloc(line, line_length + 2); // 1 for current char, 1 for null
            line[line_length] = file_content[line_offset + current_char];
            line_length++;
            current_char++;
        }

        // in case of an empty line, this will allocated enough for it
        line = realloc(line, line_length + 1);
        line[line_length] = '\0';

        // if the line has just spaces or whatever
        if (line_length > 0 && line[line_length - 1] == '\r')
        {
            line[--line_length] = '\0';
        }

        // if the line is not blank, add it to tokens
        if (!is_line_blank(line))
        {

            int column_num = 1; // start at 1

            while (*line)
            {
                int matched_any = 0;
                int match_found = 0;

                for (size_t i = 0; i < rule_count; i++)
                {
                    regex_t regex;
                    regmatch_t pmatch[MAX_MATCH];

                    if (regcomp(&regex, regex_rules[i].pattern, REG_EXTENDED) != 0)
                        continue; // only continue if the current pattern is legit

                    // if there is a match of the regex to the line contents (from the left)
                    if (regexec(&regex, line, MAX_MATCH, pmatch, 0) == 0 && pmatch[0].rm_so == 0)
                    {
                        match_found = 1;

                        // Matched at the beginning of the string
                        int match_len = pmatch[0].rm_eo - pmatch[0].rm_so;

                        char *matched_text = malloc(match_len + 1);
                        strncpy(matched_text, line + pmatch[0].rm_so, match_len);
                        matched_text[match_len] = '\0';
                        add_token(regex_rules[i].token_name, matched_text, line_num, column_num);
                        free(matched_text);

                        column_num += match_len;
                        memmove(line, line + match_len, strlen(line) - match_len + 1);

                        regfree(&regex);
                        matched_any = 1;
                        break; // Start from the top of the rules again
                    }
                    regfree(&regex);
                }

                if (!matched_any && line[0] == ' ')
                {
                    // printf("           Space: '%c'\n", line[0]);
                    memmove(line, line + 1, strlen(line)); // Move everything 1 char left
                    column_num++;                          // we will start reading the next char
                }
                else if (!matched_any) // probably an identifier
                {
                    char tempstring[256] = {0};
                    int id_len = 0;

                    while (isalnum(line[id_len]) || line[id_len] == '_')
                    {
                        tempstring[id_len] = line[id_len];
                        id_len++;
                    }

                    if (id_len > 0)
                    {
                        if (id_len > 0)
                        {
                            tempstring[id_len] = '\0';                               // terminate correctly
                            add_token(identifier, tempstring, line_num, column_num); // pass the whole thing
                            column_num += id_len;
                            memmove(line, line + id_len, strlen(line) - id_len + 1);
                        }
                    }

                    else
                    {
                        printf("Unknown token at line %d, character %d: '%c'\n", line_num, column_num, line[0]);
                        memmove(line, line + 1, strlen(line)); // skip unknown char
                    }
                }
            }
        }

        free(line);

        if (file_content[line_offset + current_char] == '\0')
        {
            break;
        }

        // we are about to start reading the next line
        line_num++;
        line_offset += current_char + 1; // skip \n
    }

    FILE *tokens_file = fopen("tokens.json", "w");
    fprintf(tokens_file, "[\n");

    for (int i = 0; i < tokens_count; i++)
    {
        fprintf(tokens_file, "  {\n");
        fprintf(tokens_file, "    \"type\": \"%s\",\n", token_type_to_string(tokens[i].type));

        fprintf(tokens_file, "    \"value\": \"");
        for (const char *p = tokens[i].value; *p; p++)
        {
            if (*p == '\"')
            {
                fprintf(tokens_file, "\\\"");
            }
            else if (*p == '\\')
            {
                fprintf(tokens_file, "\\\\");
            }
            else
            {
                fputc(*p, tokens_file);
            }
        }
        fprintf(tokens_file, "\",\n");

        fprintf(tokens_file, "    \"line\": \"%d\",\n", tokens[i].line);
        fprintf(tokens_file, "    \"character\": \"%d\"\n", tokens[i].character);

        if (i == tokens_count - 1)
            fprintf(tokens_file, "  }\n"); // No comma for the last element
        else
            fprintf(tokens_file, "  },\n");
    }

    fprintf(tokens_file, "]\n");

    fclose(tokens_file);

    for (int i = 0; i < tokens_count; i++)
    {
        free(tokens[i].value);
    }

    free(tokens);
}