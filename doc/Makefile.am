# Generate a ERP Diagram from the database schema
DOT=/usr/bin/dot
AUTODOC=/usr/bin/postgresql_autodoc

DATABASE = daisyproducer_dev
TABLES = documents_attachment,documents_document,documents_version,documents_state,documents_state_next_states,documents_state_responsible,auth_group,auth_user,auth_user_groups

DOCUMENTS = daisyproducer_dev stateMachine
DOTS_GENERATED = $(addsuffix .dot,$(filter-out stateMachine,$(DOCUMENTS)))
PDFS = $(addsuffix .pdf,$(DOCUMENTS))
PNGS = $(addsuffix .png,$(DOCUMENTS))

EXTRA_DIST = $(PDFS) $(PNGS)

%.dot:
	$(AUTODOC) -d $(DATABASE) -t dot --table=$(TABLES)

%.png: %.dot
	$(DOT) -Tpng $< > $@

%.svg: %.dot
	$(DOT) -Tsvg $< > $@

%.pdf: %.dot
	$(DOT) -Tpdf $< > $@

all: $(PDFS) $(PNGS)

clean-local:
	rm -rf $(PDFS) $(PNGS) $(DOTS_GENERATED)
