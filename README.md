# Q&A NLP Sprachmodell für die ECU-Test Dokumentation
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

