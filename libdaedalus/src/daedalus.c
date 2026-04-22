#include "daedalus.h"

#include <zmq.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>

void halt_enclave(void* stop_token);
void spawn_enclave(void* socket, void** stop_token);

static const int CONNECT_RETRY = 50;

struct daedalus_ctx
{
    void* stop_token;
    void* client_socket;
    void* zmq_context;
    pthread_t sim_thread;
};

void* simulation(void* _context) {
    struct daedalus_ctx* context = (struct daedalus_ctx*)_context;
    void *socket = zmq_socket(context->zmq_context, ZMQ_PAIR);
    
    zmq_bind(socket, "inproc://simulation");

    spawn_enclave(socket, &context->stop_token);
    
    zmq_close(socket);
    
    return _context;
}

void* connect_client(void* context) {
    void *socket = zmq_socket(context, ZMQ_PAIR);
    long sleep_interval = 200000;

    int connected = 0;
    for(int i = 0; i < CONNECT_RETRY; i++) {        
        if(zmq_connect(socket, "inproc://simulation") == 0) {
            connected = 1;
            break;
        }
        
        usleep(sleep_interval);
    }

    if(!connected) {
        zmq_close(socket);
        return NULL;
    }

    return socket;
}


struct daedalus_ctx* create_enclave_session() {
    struct daedalus_ctx* ctx = malloc(sizeof(struct daedalus_ctx));
    ctx->stop_token = 0;

    ctx->zmq_context = zmq_ctx_new();

    pthread_create(&ctx->sim_thread, NULL, simulation, ctx);

    void* client_socket = connect_client(ctx->zmq_context);

    if(!client_socket) {
        halt_enclave(ctx->stop_token);
        pthread_join(ctx->sim_thread, NULL);
        zmq_ctx_destroy(ctx->zmq_context);
        free(ctx);
        return NULL;
    }

    ctx->client_socket = client_socket;

    return ctx;
}


void shutdown_enclave(struct daedalus_ctx* ctx) {
    if(!ctx->stop_token)
        return;

    halt_enclave(ctx->stop_token);
    pthread_join(ctx->sim_thread, NULL);
    zmq_close(ctx->client_socket);
    zmq_ctx_destroy(ctx->zmq_context);
    
    free(ctx);
}

void write_enclave(struct daedalus_ctx* ctx, uint8_t* data, size_t write_len) {
    zmq_send(ctx->client_socket, data, write_len, 0);
}

size_t read_enclave(struct daedalus_ctx* ctx, uint8_t* buffer, size_t read_len) {
    return zmq_recv(ctx->client_socket, buffer, read_len, ZMQ_DONTWAIT);
}
