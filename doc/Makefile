DOT=/usr/bin/dot
AUTODOC=/usr/bin/postgresql_autodoc

DATABASE = daisyproducer_dev
TABLES = documents_attachment,documents_document,documents_version,auth_group,auth_user,auth_user_groups

DOCUMENTS = daisyproducer_dev stateMachine
DOTS_GENERATED = $(addsuffix .dot,$(filter-out stateMachine,$(DOCUMENTS)))
PDFS = $(addsuffix .pdf,$(DOCUMENTS))
PNGS = $(addsuffix .png,$(DOCUMENTS))

%.dot:
	$(AUTODOC) -d $(DATABASE) -t dot --table=$(TABLES)

%.png: %.dot
	$(DOT) -Tpng $< > $@

%.svg: %.dot
	$(DOT) -Tsvg $< > $@

%.pdf: %.dot
	$(DOT) -Tpdf $< > $@

all: $(PDFS) $(PNGS)

clean:
	rm -rf $(PDFS) $(PNGS) $(DOTS_GENERATED)
