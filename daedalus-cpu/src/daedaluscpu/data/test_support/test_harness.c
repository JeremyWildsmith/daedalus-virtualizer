#include <daedalus.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>

const char* END_TEST_KEYWORD = "!!!TEST_END!!!\n";

void repl_loop(struct daedalus_ctx* ctx) {
    int end_test_keyword_idx = 0;
    
    for(;;) {
        uint8_t buffer[1024];
        int n = read_enclave(ctx, buffer, sizeof(buffer) - 1);

        if(n <= 0)
            continue;

        buffer[n] = 0;

        printf("%s", buffer);
    
        for(int i = 0; i < n && end_test_keyword_idx < strlen(END_TEST_KEYWORD); i++) {
            if(buffer[i] == END_TEST_KEYWORD[end_test_keyword_idx])
                end_test_keyword_idx += 1;
            else {
                end_test_keyword_idx = buffer[i] == END_TEST_KEYWORD[0] ? 1 : 0;
            }
        }

        if(end_test_keyword_idx == strlen(END_TEST_KEYWORD))
            break;
    }
}

int main() {
    struct daedalus_ctx* ctx = create_enclave_session();
    repl_loop(ctx);
    shutdown_enclave(ctx);
    return 0;
}