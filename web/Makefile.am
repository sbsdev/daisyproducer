if HAVE_EMACS
doc_DATA = index.html
endif

CLEANFILES = $(doc_DATA)

all: $(doc_DATA)

if HAVE_RSYNC
if DEPLOY
deploy: $(doc_DATA)
	$(RSYNC) -t $(doc_DATA) *.pdf *.css $(DEPLOYMENT_URL)
endif
endif

%.html: %.org
# Pay attention that `--batch' implies `-q', so `.emacs' is *not* loaded and
# you don't get your `load-path' customizations. Hence, this loads the Emacs
# built-in version of Org-mode.
	@$(EMACS) --batch \
	--load=org-export-settings.el \
	--eval "(require 'org)" \
	--eval "(require 'org-exp)" \
	--visit=$< \
	--funcall org-export-as-html-batch

