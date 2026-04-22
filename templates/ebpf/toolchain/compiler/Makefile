COMPILER_SRC := .
DIST_DIR := ./dist
BUILD_DIR := ./build
COMPILER_TOOL := $(DIST_DIR)/compile.pyz
COMPILER_FILES := $(shell find $(COMPILER_SRC)/src -type f -print | sort) $(COMPILER_SRC)/Makefile $(COMPILER_SRC)/pyproject.toml
all: $(COMPILER_TOOL)

$(COMPILER_TOOL): $(COMPILER_FILES) $(DIST_DIR)
	shiv -c riscobf-compile -o $(COMPILER_TOOL) $(COMPILER_SRC)

$(DIST_DIR):
	mkdir -p $(DIST_DIR)

clean:
	rm -rf $(DIST_DIR) $(BUILD_DIR)
	rm -rf build/ dist/ .eggs/
	find . -name '*.egg-info' -prune -exec rm -rf {} +
	find . -name '*.egg' -type f -exec rm -f {} +
	find . -name '__pycache__' -prune -exec rm -rf {} +

