%{
#include <stdio.h>
%}

DIGIT      [0-9]
ID         [a-zA-Z][a-zA-Z0-9]*

%%

"int"            { printf("KEYWORD\n"); }
{ID}             { printf("IDENTIFIER\n"); }
{DIGIT}+         { printf("NUMBER\n"); }
"+"              { printf("PLUS\n"); }
"-"              { printf("MINUS\n"); }
"*"              { printf("MULTIPLY\n"); }
"/"              { printf("DIVIDE\n"); }
"="              { printf("ASSIGN\n"); }
";"              { printf("SEMICOLON\n"); }

[ \t\n]          { /* ignore */ }

.                { printf("INVALID\n"); }

%%

int yywrap(){
    return 1;
}

int main() {
    yylex();
    return 0;
}

