
GIT = /usr/bin/git
GZIP = /bin/gzip

%.tgz:
	$(GIT) archive --format=tar --prefix=$*/ HEAD | $(GZIP) > $@

all: dist

dist: daisyproducer.tgz
