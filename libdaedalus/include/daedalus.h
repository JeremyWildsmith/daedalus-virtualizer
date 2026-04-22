#pragma once

#include <stdint.h>
#include <stddef.h>

struct daedalus_ctx;

struct daedalus_ctx* create_enclave_session();
void shutdown_enclave(struct daedalus_ctx* ctx);

void write_enclave(struct daedalus_ctx* ctx, uint8_t* data, size_t write_len);
size_t read_enclave(struct daedalus_ctx* ctx, uint8_t* data, size_t read_len);