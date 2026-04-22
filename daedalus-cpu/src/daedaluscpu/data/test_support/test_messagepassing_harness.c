#include <daedalus.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>

#include <poll.h>
#include <unistd.h>
#include <stdio.h>

#include <termios.h>
#include <unistd.h>

char input_buffer[1024];
int input_buffer_length = 0;
int input_buffer_offset = 0;

int is_data_ready()
{
    struct pollfd pfd = {
        .fd = STDIN_FILENO,
        .events = POLLIN
    };

    int ret = poll(&pfd, 1, 0);

    return ret > 0 && (pfd.revents & POLLIN);
}

int read_data(char* dest, int* got_newline) {
    *got_newline = 0;

    if(input_buffer_length == 0 || input_buffer_offset == input_buffer_length) {
        input_buffer_length = 0;
        input_buffer_offset = 0;
            
        if(!is_data_ready())
            return 0;
        
        int r = read(STDIN_FILENO, input_buffer, sizeof(input_buffer));

        if(r <= 0)
            return 0;

        input_buffer_length = r;
    }
    
    int ch = input_buffer[input_buffer_offset++];
    
    if(ch == '\r') {
        return 0;
    } else if(ch == '\n') {
        *dest = 0;
        *got_newline = 1;
        return 1;
    } else {
        *dest = (char)ch;
    }

    return 1;
}

const char* END_TEST_KEYWORD = "!!!TEST_END!!!\n";

void repl_loop(struct daedalus_ctx* ctx) {
    char writedata[1024];
    int end_test_keyword_idx = 0;
    int write_offset = 0;
    for(;;) {
        int send_data = 0;
        uint8_t buffer[1024];
        int n = read_enclave(ctx, buffer, sizeof(buffer) - 1);
        
        if(write_offset < sizeof(writedata) && read_data(&writedata[write_offset], &send_data)) {
            write_offset++;
        }

        if(send_data && write_offset > 0) {
            write_enclave(ctx, writedata, write_offset);
            write_offset = 0;
        }

        if(n > 0) {
            buffer[n] = 0;

            printf("%s", buffer);
            fflush(stdout);
        
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
}

int main() {
    //Prevent input buffering
    struct termios mode;
    tcgetattr(STDIN_FILENO, &mode);
    mode.c_lflag &= ~(ICANON );
    tcsetattr(STDIN_FILENO, TCSANOW, &mode);
    setvbuf(stdout, NULL, _IOLBF, 0);

    struct daedalus_ctx* ctx = create_enclave_session();
    printf("input ready\n");
    repl_loop(ctx);
    shutdown_enclave(ctx);
    return 0;
}