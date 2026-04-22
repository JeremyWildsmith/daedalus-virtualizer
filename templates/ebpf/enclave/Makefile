COMPILER_TOOL ?=
ISA ?=

SRC_DIR = .
SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJ_DIR = obj
TOOLS_DIR = tools

all: $(OBJ_DIR)/firmware.c

$(OBJ_DIR)/firmware.c: $(OBJ_DIR)/firmware.bin
	xxd -i $(OBJ_DIR)/firmware.bin > $(OBJ_DIR)/firmware.c

$(OBJ_DIR)/firmware.bin: $(SRCS) $(COMPILER_TOOL) $(OBJ_DIR)
	$(COMPILER_TOOL) $(SRCS) --output $(OBJ_DIR)/firmware.bin

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(TOOLS_DIR):
	mkdir -p $(TOOLS_DIR)

clean:
	rm -rf $(OBJ_DIR) $(TOOLS_DIR)
