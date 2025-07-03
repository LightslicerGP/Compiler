#include <iostream>
#include <fstream>
#include <string>

using namespace std;

enum class TokenType
{
    Comment,
    Keyword,
    // ==, +=, ++, -, % and whatnot
    Number,
    String
};

struct Token
{
    TokenType type;
    string value;
    int line;
    int column;

    Token(TokenType t, const string &v, int l, int c)
        : type(t), value(v), line(l), column(c) {}
};

int main(void)
{
    ifstream file("ExampleCode.cpp");

    if (!file.is_open())
    {
        cerr << "Error: Could not open ExampleCode.cpp" << endl;
        return 1;
    }

    Token t(TokenType::Comment, "myVar", 1, 5);
    cout << "Token: " << t.value << " at line " << t.line << ", column " << t.column << endl;

    file.close();
}
