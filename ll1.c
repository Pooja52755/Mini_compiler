#include <stdio.h>

int main() {

    printf("LL(1) Parsing Table\n\n");

    printf("Grammar:\n");
    printf("E  -> T E'\n");
    printf("E' -> + T E' | ε\n");
    printf("T  -> F T'\n");
    printf("T' -> * F T' | ε\n");
    printf("F  -> (E) | id\n\n");

    printf("Parsing Table:\n\n");

    printf("Non-Terminal\t id\t +\t *\t (\t )\t $\n");
    printf("------------------------------------------------------\n");
    printf("E\t\t T E'\t -\t -\t T E'\t -\t -\n");
    printf("E'\t\t -\t + T E'\t -\t -\t ε\t ε\n");
    printf("T\t\t F T'\t -\t -\t F T'\t -\t -\n");
    printf("T'\t\t -\t ε\t * F T'\t -\t ε\t ε\n");
    printf("F\t\t id\t -\t -\t (E)\t -\t -\n");

    return 0;
}