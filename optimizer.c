#include <stdio.h>

int main() {
    int a, b;

    printf("Enter constant expression (e.g. 2 3): ");
    scanf("%d %d", &a, &b);

    printf("\nBefore Optimization:\n");
    printf("x = %d + %d\n", a, b);

    printf("\nAfter Constant Folding:\n");
    printf("x = %d\n", a + b);

    return 0;
}