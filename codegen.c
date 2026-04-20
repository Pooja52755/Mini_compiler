#include <stdio.h>

int main() {
    char a, b;

    printf("Enter expression (format: a+b): ");
    scanf(" %c+%c", &a, &b);

    printf("\nAssembly Code:\n");
    printf("MOV R1, %c\n", a);
    printf("ADD R1, %c\n", b);
    printf("MOV RESULT, R1\n");

    return 0;
}