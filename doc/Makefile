PLANTUML = java -jar ~/lib/plantuml.jar

all: state_diagram.png context_diagram.png container_diagram.png container_diagram_with_braille_corpus.png

%.png: %.txt
	${PLANTUML} $<


