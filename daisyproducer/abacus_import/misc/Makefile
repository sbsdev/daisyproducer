PLANTUML=plantuml

diagrams_src := activityDiagram.txt
diagrams := $(diagrams_src:.txt=.svg)

.PHONY: all clean

%.png: %.txt
	$(PLANTUML) $<

%.svg: %.txt
	$(PLANTUML) -tsvg $<

all: $(diagrams)

clean:
	rm -rf $(diagrams)
