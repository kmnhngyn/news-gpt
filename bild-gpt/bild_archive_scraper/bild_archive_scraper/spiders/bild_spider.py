import os
import time
import csv
import scrapy
from fpdf import FPDF

class BildSpider(scrapy.Spider):
    name = "bild_spider"

    # Liste von Datumswerten
    dates = ["2016-12-19", "2016-12-20", "2016-12-21", "2016-12-22", "2016-12-23"]

    # URLs basierend auf den Datumswerten
    start_urls = [f"https://www.bild.de/themen/uebersicht/archiv/archiv-82532020.bild.html?archiveDate={date}" for date in dates]

    # Unerwünschte Kategorien
    unwanted_categories = ['sport', 'geld', 'spiele', 'rezepte', 'lifestyle', 'bild-plus']

    # Funktion zum Filtern und Speichern der Links,
    # anschließend Aufrufen der Funktion zum Scrapen pro Link
    def parse(self, response):
        parent_folder = '../training_set'

        # Wenn Ordner training_set noch nicht vorhanden, dann erstellen
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)

        # Datum aus der URL extrahieren
        archive_date = response.url.split('=')[-1]

        # Artikel-Links auf Archivseite extrahieren
        links = response.xpath('/html/body/div/div/div[3]/main/section/div/div[2]/section/ul/li/article/a/@href').getall()

        # Links filtern, sodass Links mit unwanted_categories wegfallen
        filtered_links = self.filter_links(links)

        print('All links: ', len(links))
        print('Filtered links: ', len(filtered_links))

        # Speichern aller Links in einer CSV-Datei
        csv_file_path_all = os.path.join(parent_folder, 'all_links.csv')
        with open(csv_file_path_all, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["link"])
            for link in links:
                writer.writerow([link])

        # Speichern nur gefilterter Links in einer CSV-Datei
        csv_file_path_filtered = os.path.join(parent_folder, 'filtered_links.csv')
        with open(csv_file_path_filtered, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["link"])
            for link in filtered_links:
                writer.writerow([link])

        # Herunterladen der gefilterten Artikel
        for i, link in enumerate(filtered_links):
            full_link = 'https://www.bild.de' + link
            yield scrapy.Request(full_link, callback=self.parse_article, meta={'archive_date': archive_date, 'index': i, 'parent_folder': parent_folder, 'link': link})


    # Funktion zum parsen pro Artikel, Extrahieren der Textbausteine und Speichern als PDF
    def parse_article(self, response):
        archive_date = response.meta['archive_date']
        index = response.meta['index']
        parent_folder = response.meta['parent_folder']
        link = response.meta['link']

        # Titel extrahieren
        title_parts = response.xpath('//h2/span/text()').getall()
        title = ' '.join(title_parts) if title_parts else "No Title"

        # Datum und Uhrzeit extrahieren
        date_time = response.xpath('//time/text()').get(default="No Date and Time")

        # Artikeltext extrahieren
        article_paragraphs = response.xpath('//div[@class="article-body"]//p/text()').getall()
        article_text = '\n'.join(article_paragraphs)

        # Kategorie aus dem Link extrahieren für Dateinamen
        category = self.extract_category_from_link(link)

        # PDF-Dateiname erstellen aus Datum, Index, Kategorie und ersten 3 Wörter vom Link
        pdf_fileName = f"{archive_date}_{index + 1:02d}_{category}_{'-'.join(link.rsplit('/', 1)[-1].split('-')[:3])}.pdf"
        file_path = os.path.join(parent_folder, pdf_fileName)

        # Artikel als PDF speichern
        self.generate_pdf_from_texts(title, date_time, article_text, file_path)

        print(f"Downloaded and saved as: {pdf_fileName}")
        # 5 Sekunden warten, um Überlastung und too many requests zu vermeiden
        time.sleep(5)


    # Funktion zum Filtern der Links: nur Links scrapen, die nicht in unwanted_categories sind
    # Parameter:    links - Alle Links, die auf einer Archivseite gefunden wurden
    # Rückgabe:     filtered_links - Links, die nicht zu unwanted_categories gehören
    def filter_links(self, links):
        filtered_links = []
        for link in links:
            category = link.split('/')[1]
            if category not in self.unwanted_categories:
                filtered_links.append(link)
        return filtered_links


    # Funktion zur Extraktion der Kategorie aus dem Link
    # Parameter:    link - Link wie z.b. /regional/ein-artikel
    # Rückgabe:     parts[1] / unknown - Der erste Part des Links, da dieser die Kategorie beschreibt
    #                oder "unknown", wenn Extrahieren aus String nicht möglich
    def extract_category_from_link(self, link):
        parts = link.split('/')
        if len(parts) > 1:
            return parts[1]
        return "unknown"  # Fallback, falls Kategorie nicht erkannt wird


    # Funktion zum Bereinigung von Sonderzeichen im Text
    # Parameter:    text - Textbaustein aus dem Artikel z.b. Titel
    # Rückgabe:     text - Bereinigter Text
    def sanitize_text(self, text):
        # Bestimmte Zeichen ersetzen, die eventuell für Kontext relevant sind
        replacements = {
            '\u201c': '"',      # “ - Right Double Quotation Mark
            '\u201d': '"',      # " - Right Double Quotation Mark
            '\u201e': '"',      # „ - Left Double Quotation Mark
            '\u2060': ' ',      # Word Joiner - a zero width non-breaking space
            '\u2013': '-',      # – - En Dash
            '\u2014': '--',     # — - Em Dash
            '\u2018': "'",      # ' - Left Single Quotation Mark
            '\u2019': "'",      # ' - Right Single Quotation Mark
            '\u2022': '*',      # • - Bullet
            '\u2026': '...'     # … - Horizontal Ellipsis
        }

        # Im übergebenen Text jedes Zeichen durch Zeichen ersetzen, welches in replacements festgelegt wurde
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)

        try:
            # Encodieren in latin-1
            text = text.encode('latin-1', 'replace').decode('latin-1')
        except UnicodeEncodeError as e:
            print(f"Fehler bei latin-1 Encoding: {str(e)}")
            try:
                # Wenn latin-1 fehlschlägt, versuche utf-8
                text = text.encode('utf-8', 'ignore').decode('utf-8')
            except UnicodeEncodeError as e:
                print(f"Fehler bei utf-8 Encoding: {str(e)}")
                return text  # Falls alles fehlschlägt, Originaltext zurückgeben

        return text


    # Funktion zum Generieren der PDF und Speichern im hinterlegten Pfad
    # Parameter:    title, date_time, article_text, pdf_path - Textabschnitte aus Artikel
    def generate_pdf_from_texts(self, title, date_time, article_text, pdf_path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        # Titel hinzufügen
        pdf.multi_cell(0, 10, txt=self.sanitize_text(title), align='C')
        pdf.ln()

        # Datum und Uhrzeit hinzufügen
        pdf.multi_cell(0, 10, txt=self.sanitize_text(date_time))
        pdf.ln()

        # Haupttext hinzufügen
        pdf.multi_cell(0, 10, txt=self.sanitize_text(article_text))
        pdf.ln()

        # PDF speichern
        pdf.output(pdf_path)
