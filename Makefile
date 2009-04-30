
GIT = /usr/bin/git
GZIP = /bin/gzip

TARBALL = daisyproducer.tgz

%.tgz:
	$(GIT) archive --format=tar --prefix=$*/ HEAD | $(GZIP) > $@

all: dist

dist: $(TARBALL)

clean:
	rm -rf $(TARBALL)
