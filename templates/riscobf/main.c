#include <daedalus.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <ncurses.h>


void repl_loop(struct daedalus_ctx* ctx) {
    while(true) {
        uint8_t buffer[1024];
        int n = read_enclave(ctx, buffer, sizeof(buffer) - 1);
        buffer[n] = 0;

        if(n > 0) {
            printw("%s", buffer);
            refresh();
        } else {
            int c = getch();

            if(c != ERR) {
                printw("%c", c);
                refresh();
                
                write_enclave(ctx, (uint8_t*)&c, sizeof(uint8_t));
            }
        }
    }
}

int main() {
    initscr();

    nodelay(stdscr, TRUE);
    noecho();
    scrollok(stdscr, TRUE);

    nl(); 

    refresh();
    sleep(3);
    
    // Create a single ZMQ context shared by all threads
    struct daedalus_ctx* ctx = create_enclave_session();

    repl_loop(ctx);
    return 0;
}