# ----------------------------------------------------------------------------------------------------------------- #
# ---  ezExpress v1.0.6                                                                                         --- #
# ---                                                                                                           --- #
# ---  Modul : create_PDF                                                                                       --- #
# ---                                                                                                           --- #
# ---  Ausgelagerte Methode zur Erstellung einer PDF-Datei aus einem erstellten Einkaufszettel                  --- #
# ---                                                                                                           --- #
# ---                                                                                                           --- #
# ---  Das Modul wurde in Python (Version 3.8.6) geschrieben. Folgende externe Bibliotheken wurden benutzt:     --- #
# ---                                                                                                           --- #
# ---  - pdfgen            (https://github.com/shivanshs9/pdfgen-python)                                        --- #
# ---                      (Lizenz: https://opensource.org/licenses/MIT)                                        --- #
# ---                                                                                                           --- #
# ---  Lizenzinformation:                                                                                       --- #
# ---                                                                                                           --- #
# ---  Das Programm ezExpress wird under der Apache License, Version 2.0 veröffentlicht.                        --- #
# ---  (http://www.apache.org/licenses/LICENSE-2.0.html)                                                        --- #
# ---                                                                                                           --- #
# ---  Bei Fragen, gefundenen Fehlern oder Verbesserungsvorschlägen bitte eine Email schreiben.                 --- #
# ---                                                                                                           --- #
# ---  mailto: alexandermielke@t-online.de                                                                      --- #
# ---                                                                                                           --- #
# ---  Alexander Mielke, November 2020                                                                          --- #
# ---                                                                                                           --- #
# ----------------------------------------------------------------------------------------------------------------- #

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.colors import white


def create_PDF_File(Title, ShoppingList, TotalPrice, FilenamePDF):
    max_zeilen = 40
    seite = 1

########################### Internal Methods ###############################

    def convert_f2s(wert: float):
        if type(wert) is float:
            preis = str(wert)
            test = preis.split('.')
            if len(test[1]) == 1:
                test[1] += '0'
            elif len(test[1]) > 2:
                test[1] = test[1][:2]
            preis = test[0] + ',' + test[1] + ' €'
        else:
            preis = ''
        return preis

    def gehezu(nummer):
        y = 805 - nummer*20
        return y

    def schreibe_Ueberschrift(zeile, title):
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(0.0, 0.0, 0.0)
        c.drawString(20, gehezu(zeile), title)

    def schreibe_Seite(seite):
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.drawRightString(570, 30, '©2020 Alexander Mielke  -   Seite '+str(seite))

    def schreibe_Kategorie(zeile, align, cat):
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.5, 0.2, 0.1)
        if align == 'left':
            c.drawString(45, gehezu(zeile), cat)
            linie = c.beginPath()
            c.setLineWidth(1)
            c.setStrokeColorRGB(0.4, 0.4, 0.4)
            linie.moveTo(20, gehezu(zeile)-4)
            linie.lineTo(280, gehezu(zeile)-4)
            linie.close
            c.drawPath(linie)
        if align == 'right':
            c.drawString(335, gehezu(zeile), cat)
            linie = c.beginPath()
            c.setLineWidth(1)
            c.setStrokeColorRGB(0.4, 0.4, 0.4)
            linie.moveTo(310, gehezu(zeile)-4)
            linie.lineTo(570, gehezu(zeile)-4)
            linie.close
            c.drawPath(linie)

    def schreibe_Laden(zeile, align, shop):
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(0.1, 0.5, 0.1)
        if align == 'left':
            c.drawString(20, gehezu(zeile)-5, shop)
        if align == 'right':
            c.drawString(310, gehezu(zeile)-5, shop)

    def schreibe_Zeile(zeile, align, inhalt):
        if type(inhalt[1]) == int:
            if align == 'left':

                c.setFont("Helvetica", 8)
                c.setFillColorRGB(0.0, 0.0, 0.0)
                form = c.acroForm
                form.checkbox(x=20, y=gehezu(zeile)-4, size=14, buttonStyle='cross', fillColor=white)
                c.drawRightString(53, gehezu(zeile), str(inhalt[1])+'x')
                c.drawString(55, gehezu(zeile), inhalt[2][:35]+', '+inhalt[3])
                c.setFillColorRGB(0.3, 0.3, 0.6)
                c.drawRightString(280, gehezu(zeile), convert_f2s(inhalt[4]))

            elif align == 'right':

                c.setFont("Helvetica", 8)
                c.setFillColorRGB(0.0, 0.0, 0.0)
                form = c.acroForm
                form.checkbox(x=310, y=gehezu(zeile)-4, size=14, buttonStyle='cross', fillColor=white)
                c.drawRightString(343, gehezu(zeile), str(inhalt[1])+'x')
                c.drawString(345, gehezu(zeile), inhalt[2][:35]+', '+inhalt[3])
                c.setFillColorRGB(0.3, 0.3, 0.6)
                c.drawRightString(570, gehezu(zeile), convert_f2s(inhalt[4]))

################################# Code #####################################

    c = canvas.Canvas(FilenamePDF, pagesize=pagesizes.A4)
    c.setTitle(Title+' - ezExpress')
    schreibe_Ueberschrift(0, Title)
    ausrichtung = 'left'
    aktzeile = 1

    for row in range(len(ShoppingList)):

        if ShoppingList[row][0] == 'Laden':
            schreibe_Laden(aktzeile, ausrichtung, ShoppingList[row][2])
        elif ShoppingList[row][0] == 'Kategorie':
            schreibe_Kategorie(aktzeile, ausrichtung, ShoppingList[row][2])
        else:
            schreibe_Zeile(aktzeile, ausrichtung, ShoppingList[row])

        if aktzeile >= max_zeilen-3:
            if ausrichtung == 'left':
                ausrichtung = 'right'
                aktzeile = 0
            else:
                schreibe_Seite(seite)
                c.showPage()
                ausrichtung = 'left'
                aktzeile = 0
                seite += 1
        aktzeile += 1

    if ausrichtung == 'left':
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.3, 0.3, 0.6)
        c.drawRightString(280, gehezu(aktzeile)-5, 'berechneter Gesamtpreis : '+TotalPrice)
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawRightString(280, gehezu(aktzeile+1)+3, 'zuzüglich eventuell anfallendem Pfand!')
    else:
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.3, 0.3, 0.6)
        c.drawRightString(570, gehezu(aktzeile)-5, 'berechneter Gesamtpreis : '+TotalPrice)
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawRightString(570, gehezu(aktzeile+1)+3, 'zuzüglich eventuell anfallendem Pfand!')

    schreibe_Seite(seite)
    c.showPage()
    c.save()
