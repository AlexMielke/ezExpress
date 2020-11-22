# ezExpress 1.1.0

ezExpress ist ein Programm zum Erstellen eines Einkaufszettels mit Artikeln eines Produktkataloges. 

Ein Produktkatalog kann von Hand selber erstellt oder vom deutschen Internetanbieter https://www.discounter-preisvergleich.de/ per WebCrawler erstellt werden. 
Beim letzteren stehen mehrere deutsche Discounter zur Auswahl. Die Produktkataloge können nach Belieben verändert und dann gespeichert werden. 
Ein Produktkatalog wird in einer selbsterschaffenen Baumstruktur erstellt um eine Abhängigkeit von SQL und die damit verbundenen Software-/Netzwerkinstallationen zu vermeiden.
Der mit ezExpress erstellte Einkaufszettel kann ausgedruckt, als PDF-Datei gespeichert oder per Email zum Beispiel an ein Mobiltelefon versendet werden. Die PDF-Dateien beinhalten Checkboxen, um somit den Einkauf zu erleichtern.


Das Programm wurde in Python (Version 3.8.6) geschrieben. Folgende externe Bibliotheken wurden benutzt:

- Requests (https://requests.readthedocs.io/de/latest/index.html) 

- BeautifulSoup4 (https://www.crummy.com/software/BeautifulSoup/)

- cryptography (https://github.com/pyca/cryptography)

- pdfgen (https://github.com/shivanshs9/pdfgen-python)

- PIL/Pillow (https://python-pillow.org/)

- pdf2image (https://github.com/Belval/pdf2image)

- PyQt5 (https://www.riverbankcomputing.com/software/pyqt/)

- lxml (https://github.com/lxml/lxml)


Lizenzinformation:
Das Programm ezExpress wird under der Apache License, Version 2.0 veröffentlicht.
(http://www.apache.org/licenses/LICENSE-2.0.html)
