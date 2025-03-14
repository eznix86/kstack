EXAMPLES_DIR := examples

EXAMPLES := $(wildcard examples/*.yaml)

all: validate

validate: $(EXAMPLES)
	@for file in $^; do \
		kstack validate "$$file"; \
	done

.PHONY: all validate
