#include <stdio.h>
#include <stdlib.h>

int main() {

    printf("Mini Compiler Execution:\n\n");

    printf("1. Running Lexer:\n");
    system("./lexer < input.txt");

    printf("\n2. Running Parser:\n");
    system("./parser");

    printf("\n3. LL1 Table:\n");
    system("./ll1");

    printf("\n4. SLR Table:\n");
    system("./slr");

    printf("\n5. Intermediate Code:\n");
    system("./inter");

    printf("\n6. Optimization:\n");
    system("./opt");

    printf("\n7. Code Generation:\n");
    system("./codegen");

    return 0;
}