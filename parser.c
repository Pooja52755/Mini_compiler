#include <stdio.h>
#include <ctype.h>

char input[100];
int i = 0;

void E();
void T();
void F();

void match(char c) {
    if (input[i] == c) i++;
    else {
        printf("Error\n");
    }
}

void E() {
    T();
    while (input[i] == '+') {
        match('+');
        T();
    }
}

void T() {
    F();
    while (input[i] == '*') {
        match('*');
        F();
    }
}

void F() {
    if (isalnum(input[i])) {
        i++;
    } else if (input[i] == '(') {
        match('(');
        E();
        match(')');
    } else {
        printf("Error\n");
    }
}

int main() {
    printf("Enter expression: ");
    scanf("%s", input);
    E();

    if (input[i] == '\0')
        printf("Valid Expression\n");
    else
        printf("Invalid Expression\n");

    return 0;
}