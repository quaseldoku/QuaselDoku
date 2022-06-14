# Q&A NLP Sprachmodell für die ECU-Test Dokumentation

![](/Fast_Demo.gif)

Diese Projekt stellt eine Möglichkeit vor, wie mittels NLP Suchanfragen für die ECU-Test Dokumentation verarbeitet werden können. Um das finale Ergebnis zu betrachen,
reicht es das hier vorhandene Docker-Image auszuführen. Für die Betrachtung der einzelnen Arbeitsschritte bis zum finalen Ergebnis und zur Evaluierung der einzelnen Schritte
können über Kedro verschiedene Pipelines ausgeführt werden. Genauere Details über den Entstehungsprozess findet man in den Jupyter Notebooks.

## Aufgabenstellung
Ziel war die Erweiterung der Suchfunktion für die Dokumentation der TraceTronic eigenen Software ECU-TEST auf Basis von Deep-Learning Sprachmodellen.
Dazu wurde sich zunächst mit dem Datensatz vertraut gemacht, es wurden Metriken zur Bewertung der entstandenen Ergebnisse erstellt und ein passende Modelle ausgewählt.
Im Anschluss wurde eine skalierbare und erweiterbare Lösung mit Hilfe von Software-Stacks implementiert. Zum Schluss wurden die Ergebnisse evaluiert. Zusätzlich wurde 
eine Benutzerschnittstelle erstellt welche in einem Docker-Container ausgerollt wurde.

Verwendeter Technoligie-Stack:

- Git
- Python/Jupyter-Notebooks
- Kedro
- Streamlit

## Vor dem ersten Start
Bevor man das Projekt zum ersten mal ausführen kann, müssen folgende Dinge bereitgestellt werden:

- Python Version 3.8.2 ist installiert
- Poetry-Paket wurde Installiert 
- ECU-Test Dokumentation liegt vor
- OPTIONAL: Testdatensätze liegen vor

## Aufbau des Projekts

![Grobaufbau des Projekts](/Aufbau.jpg)

## Wichtige Befehle
Dieses Projekt besteht aus verschiedenen Teilkomponenten, hier sind die wichtigsten Befehle aufgelistet, um auf die Komponenten gezielt zugreifen zu können.

### Kedro pipeline
Es gibt zwei große Pipelines in diesem Projekt: Die eine dient dem Aufbau des Modells, inklusive des Parsing der Dokumentation, die andere dient der Evaluation der Modelle.

Zum Aufruf der Deploiment Pipeline kann der folgende Befehl verwendet werden:

```
kedro run --pipeline dp
```

Zum Aufruf der Test Pipeline wiederum dieser Befehl:

```
kedro run --pipeline validation
```

### Aufruf des User Interface über Docker
Dieses Projekt enthält eine minimalistische Weboberfläche, diese kann durch einen Docker Container verwendet werden. Um die Oberfläche zu starten kann die folgenden Befehle ausgeführt werden:

```
docker-compose build
```
Erzeugt ein Image, dieses sollte zu Beginn einmal erzeugt werden, um die Container darauf laufen zu lassen.

```
docker-compose up
```
Dieser Befehl aggregiert die Ausgaben der zwei Docker-Container des Projekts und ermöglicht letzten Endes ein Ausführen der Weboberfläche.

