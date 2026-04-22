LIB_NAME = libdaedalus.a

CC = gcc
AR = ar
ARFLAGS = rcs

SRC_DIR = src
OBJ_DIR = obj
INC_DIR = include

PREFIX ?= $(HOME)/.local
INCLUDE_DEST = $(PREFIX)/include
LIB_DEST = $(PREFIX)/lib
INSTALL = install

CFLAGS = -Wall -Wextra -O3 -I$(INC_DIR)

SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)
HEADERS = $(wildcard $(INC_DIR)/*.h)

all: $(LIB_NAME)

install: $(LIB_NAME)
	$(INSTALL) -d $(INCLUDE_DEST)
	$(INSTALL) -d $(LIB_DEST)
	$(INSTALL) -m 644 $(HEADERS) $(INCLUDE_DEST)
	$(INSTALL) -m 644 $(LIB_NAME) $(LIB_DEST)

$(LIB_NAME): $(OBJS)
	$(AR) $(ARFLAGS) $@ $^

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

clean:
	rm -rf $(OBJ_DIR) $(LIB_NAME)

.PHONY: all clean