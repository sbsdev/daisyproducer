PLANTUML = java -jar ~/lib/plantuml-1.2022.6.jar

all: state_diagram.png context_diagram.png container_diagram.png container_diagram_with_braille_corpus.png

%.png: %.txt
	${PLANTUML} $<


