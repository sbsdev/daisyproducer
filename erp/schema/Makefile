TRANG=trang

schemas := $(wildcard *.rnc)
schemas_rng := $(schemas:.rnc=.rng)

.PHONY: all clean

%.rng: %.rnc
	$(TRANG) $< $@

all: $(schemas_rng)

clean:
	rm -rf $(schemas_rng)
