# Makefile template for shared library

CC = gcc # C compiler
CFLAGS = -fPIC -Wall -Wextra -O3 -Werror -g # C flags
LDFLAGS = -shared # linking flags
RM = rm -f # rm command
TARGET_LIB = clib/clib.so # target lib

SRCS = $(shell echo clib/*.c) # source files
OBJS = $(patsubst %,build/%,$(notdir $(SRCS:.c=.o))) # Object files to compile
DEPS = $(OBJS:.o=.d) # Dependency files

BUILD_DIR = build

.PHONY: all
all: $(BUILD_DIR) ${TARGET_LIB}

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(TARGET_LIB): $(OBJS)
	$(CC) ${LDFLAGS} -o $@ $(OBJS)

build/%.o: clib/%.c
	$(CC) $(CFLAGS) -c $< -o $@

-include $(DEPS)

$(BUILD_DIR)/%.d: clib/%.c
	@$(CC) $(CFLAGS) -MM -MT $(@:.d=.o) $< > $@

.PHONY: clean
clean:
	${RM} ${TARGET_LIB} ${OBJS} ${DEPS}
	${RM} -r $(BUILD_DIR) # Remove the build directory
	${RM} *.pyc pylib/*.pyc
