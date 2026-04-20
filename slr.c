#include <stdio.h>

int main() {

    printf("SLR Parsing Table\n\n");

    printf("Grammar:\n");
    printf("E -> E + T\n");
    printf("E -> T\n");
    printf("T -> id\n\n");

    printf("ACTION TABLE:\n");
    printf("State\t id\t +\t $\n");
    printf("---------------------------\n");
    printf("0\t s3\t -\t -\n");
    printf("1\t -\t s4\t acc\n");
    printf("2\t -\t r2\t r2\n");
    printf("3\t -\t r3\t r3\n");
    printf("4\t s3\t -\t -\n");
    printf("5\t -\t r1\t r1\n\n");

    printf("GOTO TABLE:\n");
    printf("State\t E\t T\n");
    printf("----------------\n");
    printf("0\t 1\t 2\n");
    printf("4\t -\t 5\n");

    return 0;
}