TOOLCHAIN_COMPILER ?= ./toolchain/compile.pyz

CC := gcc
CXX := g++

ENCLAVE_FIRMWARE_DIR := ./enclave_firmware
TOOLCHAIN_PLATFORM_LIBS := ./toolchain/
ENCLAVE_BIN := ./enclave_bin
OBJ := ./obj
HOST_BIN_DIR := ./host_bin
TEST_SRC_DIR := ./test_cases

TEST_MESSAGE_PASSING_BINS_DIR := ./test_message_passing_bin
TEST_MESSAGE_PASSING_FIRMWARE_DIR := ./test_message_passing_firmware
TEST_MESSAGE_PASSING_SRC_DIR := ./test_message_passing

TEST_SRCS := $(wildcard $(TEST_SRC_DIR)/*.c)
TEST_MESSAGE_PASSING_SRCS := $(wildcard $(TEST_MESSAGE_PASSING_SRC_DIR)/*.c)

TEST_ENCLAVE_FIRMWARE := $(patsubst $(TEST_SRC_DIR)/%.c,$(ENCLAVE_FIRMWARE_DIR)/%.bin,$(TEST_SRCS))
TEST_ENCLAVE_BINS := $(patsubst $(TEST_SRC_DIR)/%.c,$(ENCLAVE_BIN)/%,$(TEST_SRCS))
TEST_HOST_BINS := $(patsubst $(TEST_SRC_DIR)/%.c,$(HOST_BIN_DIR)/%,$(TEST_SRCS))

TEST_MESSAGE_PASSING_FIRMWARE := $(patsubst $(TEST_MESSAGE_PASSING_SRC_DIR)/%.c,$(TEST_MESSAGE_PASSING_FIRMWARE_DIR)/%.bin,$(TEST_MESSAGE_PASSING_SRCS))
TEST_MESSAGE_PASSING_BINS := $(patsubst $(TEST_MESSAGE_PASSING_SRC_DIR)/%.c,$(TEST_MESSAGE_PASSING_BINS_DIR)/%,$(TEST_MESSAGE_PASSING_SRCS))

all: $(TEST_HOST_BINS) $(TEST_ENCLAVE_BINS) $(TEST_ENCLAVE_FIRMWARE) $(TEST_MESSAGE_PASSING_BINS)

$(TEST_MESSAGE_PASSING_BINS_DIR):
	mkdir -p $(TEST_MESSAGE_PASSING_BINS_DIR)

$(TEST_MESSAGE_PASSING_FIRMWARE_DIR):
	mkdir -p $(TEST_MESSAGE_PASSING_FIRMWARE_DIR)

$(ENCLAVE_FIRMWARE_DIR):
	mkdir -p $(ENCLAVE_FIRMWARE_DIR)

$(HOST_BIN_DIR):
	mkdir -p $(HOST_BIN_DIR)

$(OBJ):
	mkdir -p $(OBJ)

$(ENCLAVE_BIN):
	mkdir -p $(ENCLAVE_BIN)

$(TEST_MESSAGE_PASSING_FIRMWARE_DIR)/%.bin: $(TEST_MESSAGE_PASSING_SRC_DIR)/%.c | $(TEST_MESSAGE_PASSING_FIRMWARE_DIR)
	$(TOOLCHAIN_COMPILER) $< --include . --output $@

$(TEST_MESSAGE_PASSING_FIRMWARE_DIR)/%.c: $(TEST_MESSAGE_PASSING_FIRMWARE_DIR)/%.bin | $(TEST_MESSAGE_PASSING_FIRMWARE_DIR)
	xxd -i -n obj_firmware_bin $< >> $@

$(TEST_MESSAGE_PASSING_BINS_DIR)/%.o: $(TEST_MESSAGE_PASSING_FIRMWARE_DIR)/%.c | $(TEST_MESSAGE_PASSING_BINS_DIR) $(OBJ)/test_messagepassing_harness.o $(TEST_MESSAGE_PASSING_FIRMWARE)
	$(CC) -c $< -o $@

$(TEST_MESSAGE_PASSING_BINS_DIR)/%: $(TEST_MESSAGE_PASSING_BINS_DIR)/%.o | $(TEST_MESSAGE_PASSING_BINS_DIR) $(OBJ)/test_messagepassing_harness.o
	$(CXX) \
		$< $(OBJ)/test_messagepassing_harness.o \
		-L$(HOME)/.local/lib \
		-ldaedalus \
		$(TOOLCHAIN_PLATFORM_LIBS)/server.a \
		$(TOOLCHAIN_PLATFORM_LIBS)/platform.a \
		$(TOOLCHAIN_PLATFORM_LIBS)/verilated_runtime.a \
		-lzmq \
		-o $@


$(ENCLAVE_FIRMWARE_DIR)/%.bin: $(TEST_SRC_DIR)/%.c | $(ENCLAVE_FIRMWARE_DIR)
	$(TOOLCHAIN_COMPILER) $< --include . --output $@

$(ENCLAVE_FIRMWARE_DIR)/%.c: $(ENCLAVE_FIRMWARE_DIR)/%.bin | $(ENCLAVE_FIRMWARE_DIR)
	xxd -i -n obj_firmware_bin $< >> $@

$(HOST_BIN_DIR)/%: $(TEST_SRC_DIR)/%.c | $(HOST_BIN_DIR)
	$(CC) -DHOST_EXEC $< host_firmware.c -I. -o $@

$(OBJ)/test_harness.o : test_harness.c | $(OBJ)
	$(CC) -I$(HOME)/.local/include -c test_harness.c -o $(OBJ)/test_harness.o

$(OBJ)/test_messagepassing_harness.o : test_messagepassing_harness.c | $(OBJ)
	$(CC) -I$(HOME)/.local/include -c test_messagepassing_harness.c -o $(OBJ)/test_messagepassing_harness.o

$(ENCLAVE_BIN)/%.o: $(ENCLAVE_FIRMWARE_DIR)/%.c | $(ENCLAVE_BIN) $(OBJ)/test_harness.o $(TEST_ENCLAVE_FIRMWARE)
	$(CC) -c $< -o $@

$(ENCLAVE_BIN)/%: $(ENCLAVE_BIN)/%.o | $(ENCLAVE_BIN) $(OBJ)/test_harness.o
	$(CXX) \
		$< $(OBJ)/test_harness.o \
		-L$(HOME)/.local/lib \
		-ldaedalus \
		$(TOOLCHAIN_PLATFORM_LIBS)/server.a \
		$(TOOLCHAIN_PLATFORM_LIBS)/platform.a \
		$(TOOLCHAIN_PLATFORM_LIBS)/verilated_runtime.a \
		-lzmq \
		-o $@

clean:
	rm -rf ./obj ./enclave_bin ./enclave_firmware ./host_bin ./test_message_passing_bin ./test_message_passing_firmware