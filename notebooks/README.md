# Übersicht der Nootebooks
Hier sind alle im Projekt entstandenen Jupyter Notebooks aufgelistet und kurz beschrieben. 
In der Regel sind die Notebooks während der Recherche oder Vorarbeit neuer Funktionen entstanden, die später in die Kedro pipeline eingepflegt werden sollen.

## data_loader_test
Hier wird geprüft, ob der in der Kedro pipeline "dp" enstandene Datensatz "ecu_test_doku" geladen. Dieser Datensatz enthält die "rohen" HTML-Dateien der ECU-Test Dokumentation.
Zunächst wird überprüft, ob der Kedro Datensatz auch alle Elemente der Dokumentation enthält. Anschließend werden die Dateinamen ausgelesen und in entsprechendes Format gepackt.

## finetune_parser
Hier entsteht der Parser zum Auslesen der Daten aus den HTML-Dateien, nachdem diese aus den Ordnerstrukturen entfernt und gefiltert wurden. Dabei werden verschiedene Filter angesetzt um die relevanten Textinhalten aus den Daten zu extrahieren. In diesem Notebook finden sich auch Fehler und Lösungsvorschläge die im Laufe der Entwicklung des Parsers entstanden sind. Der Fokus lag hier lediglich auf dem Extrahieren der Textinhalte, diese werden zunächst getrennt voneinander mit Referenz auf den Paragraphen und die Quelldatei als CSV-Datei abgelegt. 

## Generate_csv
Nachdem das fehlerfreie Auslesen relevanter Texte abgeschlossen war, galt es die einzelnen Textbruchstücke zu Paragraphen zusammenzuführen mit denen ein Q&A Modell gespeist werden kann. Hier wurde eine Funktion erstellt die es ermöglicht Texte mit gleicher Paragraphenüberschrift und Quelldatei zusammen zu führen und mit einem Hash-Wert zu versehen. Im späteren Verlauf wurde ich auch eine Möglichkeit geprüft Test-Daten aus Frage-Antwort Paaren mit dem eben genannten Hash-Wert zu verknüpfen. Die so entstandenen Daten werden in CSV-Dateien abgelegt. 

## keyword_search
In diesem Notebook wird überprüft wie die Stichwortsuche aus der ECU-Test Doku am besten nachgebildet werden kann. Dazu werden hier einige Tests mit der Suchengine whoosh durchgeführt.

## keyword_search_as_pipeline
Nachdem die Stichwortsuche mit woosh erfolgreich in Kedro implementiert wurde, gilt es die Suchindexe für die ECU-Test Dokumentation zu erstellen. Diese ermöglichen die Funktion der Searchengine auf unserem Datensatz. Ebenso wird geprüft, wie ganze Fragen von der Searchengine beantwortet werden können.

## keyword_search_as_pipeline_with_model
Dies ist eine Ergänzung des vorhergehenden Notebooks und baut nun auch die Stichwortsuche das BERT-Modell auf. Hier wurde überprüft wie die beiden Modelle miteinander verbunden werden müssen, um einen reibungslosen Übergang ineinander zu gewährleisten.

## loading_squad
Für die Evaluation der Stichwortsuche, soll das Modell auf einem weiteren Datensatz getestet werden. Hierfür kommt der GERMANSQUAD Datensatz in Frage, der hier einmal ausgelesen und analysiert wurde.

## method_evaluation
In diesem Notebook entstehen die Grafiken und Tabellen der Evaluierung der Modelle. 

## parse_html
Hier wurden die HTML-Dateien nach der Exktraktion aus der ECU-Test Dokumentation Ordnerstruktur erstmalig zur kontrolle ausgelesen. Das ganze wurde zur Anschaulichkeit in einen Pandas DataFrame umgewandelt.

## parsed_doku_exploration
Dieses Notebook dient zu Sichtung der geparsten HTML-Inhalte. Die CSV-Datei mit allen Texten der ECU-Test Dokumentation wird ausgelesen und es wurde überprüft, wie sich spezielle Texte (besonders kurze Inhalte, Listeninhalte, potentielle leere Inhalte) verhalten. Anschließend wurden daraus To-Dos (bereits abgeschlossen) entwickelt.

## possible_parser
In diesem Notebook wurden Möglichkeiten zum Auslesen der HTML-Inhalte geprüft. Schnell entwickelte es sich zu einer Auflistung möglicher Beautifulsoup-Funktionen, die für den zukünftigen Parser nützlich sein könnten.

## test_data_annotation
Dieses Notebook dient zur Formulierung möglicher Test-Fragen für den ECU-Test Datensatz. Es werden zufällig Phrasen aus der geparsten Dokumentation ausgegeben zu der dann Fragen formuliert werden können. Das Frage-Antwort-Paar kann anschließend in einem CSV-File abgespeichert werden. 

## verfahrensrecherche
Hierbei handelt es sich um eine Übersichtsseite, in der mögliche Q&A Modelle und weitere mögliche Vorgehensweisen für das Projekt gesammelt werden konnten. Es enthält Informationen zu möglichen Q&A Verfahren, Gütemaßen, Ground Truth Definitionen, etc.
