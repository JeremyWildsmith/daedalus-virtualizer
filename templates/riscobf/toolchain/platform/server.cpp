#include "Vtb_femto_sdram.h"
#include "verilated_vcd_c.h"

#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <cstring>
#include <cstdlib>
#include <zmq.h>
#include <errno.h>

#include <atomic>

extern const unsigned char obj_firmware_bin[];
extern unsigned int obj_firmware_bin_len;

typedef int (*interface_read_t)(void* ctx, char* buffer, int readlen);
typedef void (*interface_write_t)(void* ctx, char data);
typedef void (*interface_shutdown_t)(void* ctx);

struct mmio_ctx {
	char buffer[1024];
	int size = 0;
	int idx = 0;
};

struct cpu_interface {
	void* ctx;
	interface_write_t write;
	interface_read_t read;
	interface_shutdown_t shutdown;
};

static void initialize_cpu(Vtb_femto_sdram* top) {
	top->clk = 0;

	for(int t = 0; t <= 200; t += 5) {
		top->clk = !top->clk;
		top->eval();
	}

	top->resetn = 1;
}

static void initialize_verilator() {
    const char* argv[] = {
        "program",
        nullptr
    };

    int argc = static_cast<int>(sizeof(argv) / sizeof(char*)) - 1;

    Verilated::commandArgs(argc, const_cast<char**>(argv));
}

static void clock_cycle(Vtb_femto_sdram *top)
{
    top->clk = 0;
    top->eval();

    top->clk = 1;
    top->eval();
}

static void load_memory(Vtb_femto_sdram* top, uint32_t baseaddr) {
	long size = obj_firmware_bin_len;

	uint8_t* buffer = (uint8_t*)&obj_firmware_bin[0];

	top->load_enable   = 0;
    top->load_addr     = 0;
    top->load_data     = 0;

    clock_cycle(top);

	for(uint32_t i = 0; i < size; i += 4) {
		uint32_t write_word = 0;

		int num_write = size - i;

		if(num_write > 4)
			num_write = 4;

		for(int bi = 0; bi < num_write; bi++) {
			write_word |= ((uint32_t)buffer[i + bi]) << ((uint32_t)(8 * bi));
		}
		
		top->load_addr = baseaddr + i;
		top->load_data = write_word;
		top->load_enable = 1;
		clock_cycle(top);

		top->load_enable = 0;
		clock_cycle(top);
	}
	
	top->load_enable = 0;
	clock_cycle(top);
}

static Vtb_femto_sdram* create_module() {
	Vtb_femto_sdram* top = new Vtb_femto_sdram;
	top->clk = 0;
	top->resetn = 0;
	top->load_enable = 0;
	top->load_addr = 0;
	top->load_data = 0;
	top->eval();

	return top;
}

static void mmio_pre_eval(Vtb_femto_sdram* top, struct mmio_ctx* ctx) {
	if(ctx->idx >= ctx->size)
	{
		// Clear the input valid flag only after it has been digested by the mmio module.
		if(top->input_ready)
			top->input_valid = 0;

		ctx->idx = 0;
		ctx->size = 0;
		return;
	}

	if(!top->clk || !top->input_ready)
		return;
	
	top->input_valid = 1;
	top->input_data = ctx->buffer[ctx->idx];
	ctx->idx++;
}

static int mmio_write(Vtb_femto_sdram* top, struct mmio_ctx* ctx, const char* data, int len) {
	int amount_to_write = sizeof(ctx->buffer) - ctx->size;

	if(len < amount_to_write)
		amount_to_write = len;

	if(amount_to_write == 0)
		return 0;

	memcpy(&ctx->buffer[ctx->size], data, amount_to_write);
	ctx->size += amount_to_write;

	return amount_to_write;
}

static int mmio_fill_size(struct mmio_ctx* ctx) {
	int amount_to_write = sizeof(ctx->buffer) - ctx->size;

	return amount_to_write;
}
static int zmq_read(void* socket, char* buffer, int readlen) {
    if (readlen <= 0)
        return 0;

    int n = zmq_recv(socket, buffer, readlen, ZMQ_DONTWAIT);

    if (n >= 0) {
        return n;
    }

    if (zmq_errno() == EAGAIN || zmq_errno() == EINTR) {
        return 0;
    }

    fprintf(stderr, "Error occurred reading from ZMQ Socket: %s\n", zmq_strerror(zmq_errno()));
    return 0;
}

static void zmq_write(void* socket, char data) {
    int n = zmq_send(socket, &data, 1, 0);

    if (n < 0) {
        int err = zmq_errno();
        
        if (err == EINTR) {
            zmq_write(socket, data);
            return;
        }

        fprintf(stderr, "Error writing to ZMQ: %s\n", zmq_strerror(err));
    }
}

static void zmq_shutdown(void* socket) {
	//Socket is closed by harness. Don't close it here...
}


static void configure_interface(struct cpu_interface* interface, void* socket) {
	interface->ctx = socket;
	interface->read = zmq_read;
	interface->write = zmq_write;
	interface->shutdown = zmq_shutdown;
}

extern "C" {

void halt_enclave(void* stop_token) {
	std::atomic<bool>* stop = (std::atomic<bool>*)stop_token;

	stop->store(true, std::memory_order_release);
}

void spawn_enclave(void* socket, void** stop_token)
{
	auto* stop = new std::atomic<bool>(false);
	*stop_token = stop;

	struct cpu_interface interface;
	configure_interface(&interface, socket);
	
	struct mmio_ctx mmio = {0};

	initialize_verilator();

	Vtb_femto_sdram* top = create_module();

	//Keep the CPU inactive while we populate the memory
	top->resetn = 0;
	load_memory(top, 0);

	initialize_cpu(top);

	unsigned long test_count = 0;
	while (!Verilated::gotFinish() && !stop->load(std::memory_order_acquire)) {
		top->clk = !top->clk;

		mmio_pre_eval(top, &mmio);
		top->eval();

		if(top->clk && top->output_data_ready) {
			interface.write(interface.ctx, top->output_data);
		}

		test_count++;

		if(test_count >= 300000) {
			int buffer_fill_size = mmio_fill_size(&mmio);

			if(buffer_fill_size > 0) {
				char buffer[sizeof(mmio.buffer)];

				int read_count = interface.read(interface.ctx, buffer, buffer_fill_size);
				mmio_write(top, &mmio, (const char*)buffer, read_count);
			}
		}
	}

	delete top;
	interface.shutdown(interface.ctx);
}

}