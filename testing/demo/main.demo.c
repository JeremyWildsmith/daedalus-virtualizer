#include <daedalus.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <stdio.h>

void read_line(struct daedalus_ctx* ctx, char* buffer, int buffer_len) {
    int i;
    for(i = 0; i < buffer_len - 1;) {
        uint8_t c;
        int n = read_enclave(ctx, &c, 1);
        if(n > 0) {
            if(c == '\n') break;
            else buffer[i++] = c;
        }
    }
    buffer[i] = 0;
}

int main() {
    char name[256];
    char key[256];
    char buffer[256];
    struct daedalus_ctx* ctx = create_enclave_session();

    printf("Welcome to the Key Verification System... System is starting up...\n");
    sleep(3);

    printf("Enter your name: ");
    fgets(name, sizeof(name) - 1, stdin);
    write_enclave(ctx, (uint8_t*)&name, strlen(name));
    printf("Enter your product key: ");
    fgets(key, sizeof(key) - 1, stdin);
    write_enclave(ctx, (uint8_t*)&key, strlen(key));

    printf("Please wait while validate your key...\n");

    read_line(ctx, buffer, sizeof(buffer));
    printf("\n");

    if(strcmp(buffer, "VALID") == 0) {
        name[strlen(name) - 1] = 0;
        key[strlen(key) - 1] = 0;
        printf("You have captured the flag! FLAG={'%s', %s}", name, key);
    } else {
        printf("Sorry, that isn't the right product key. Try again :)\n");
    }
    return 0;
}
