# Generate a ERP Diagram from the database schema

DATABASE = daisyproducer_dev
TABLES = documents_attachment,documents_document,documents_version,documents_state,documents_state_next_states,documents_state_responsible,auth_group,auth_user,auth_user_groups

DOCUMENTS = daisyproducer_dev stateMachine
DOTS_GENERATED = $(addsuffix .dot,$(filter-out stateMachine,$(DOCUMENTS)))
PDFS = $(addsuffix .pdf,$(DOCUMENTS))
PNGS = $(addsuffix .png,$(DOCUMENTS))

# Only generate a ERP Diagram from the database schema if configure found the POSTGRESQL_AUTODOC tool
if HAVE_POSTGRESQL_AUTODOC
if HAVE_DOT
  EXTRA_DIST = $(PDFS) $(PNGS) stateMachine.dot
  all: $(PDFS) $(PNGS)
endif
endif

%.dot:
	$(POSTGRESQL_AUTODOC) -d $(DATABASE) -t dot --table=$(TABLES)

%.png: %.dot
	$(DOT) -Tpng $< > $@

%.svg: %.dot
	$(DOT) -Tsvg $< > $@

%.pdf: %.dot
	$(DOT) -Tpdf $< > $@

clean-local:
	rm -rf $(PDFS) $(PNGS) $(DOTS_GENERATED)
