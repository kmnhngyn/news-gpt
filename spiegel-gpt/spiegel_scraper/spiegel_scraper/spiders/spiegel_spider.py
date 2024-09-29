import os
import time
import csv
import scrapy
from fpdf import FPDF
from urllib.parse import urljoin

class SpiegelSpider(scrapy.Spider):
    name = "spiegel_spider"
    allowed_domains = ["spiegel.de"]

    # Liste von Datumswerten
    # dates = ["19.12.2016", "20.12.2016", "21.12.2016", "22.12.2016", "23.12.2016"]
    dates = ["19.12.2016"]

    # URLs basierend auf den Datumswerten
    start_urls = [f"https://www.spiegel.de/nachrichtenarchiv/artikel-{date}.html" for date in dates]

    # Nicht gewünschte Ressorts/Kategorien festlegen, die in den URLs zu finden sind
    unwanted_categories = ['sport', 'wirtschaft', 'stil']

    # Funktion zum Filtern und Speichern der Links,
    # anschließend Aufrufen der Funktion zum Scrapen pro Link
    def parse(self, response):
        parent_folder = '../test_newscript'

        # Wenn Ordner training_set noch nicht vorhanden, dann erstellen
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)

        # Datum aus der URL extrahieren
        date_str = response.url.split('-')[-1].replace('.html', '')
        archive_date = time.strptime(date_str, "%d.%m.%Y")
        formatted_date = time.strftime("%Y-%m-%d", archive_date)

        # Artikel-Links auf Archivseite extrahieren
        links = response.xpath('//main//section//div/article/header/h2/a/@href').getall()

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
            if i >= 5:
                break
            # Verwende urljoin, um den vollständigen Link zu erhalten
            full_link = urljoin(response.url, link)

            # PDF-Dateiname aus dem Datum, Index, Kategorie und Artikel-Info erstellen
            category = self.extract_category_from_link(full_link)
            article_info = '-'.join(full_link.split('/')[-1].split('-')[:3])
            pdf_file_name = f"{formatted_date}_{i + 1:02d}_{category}_{article_info}.pdf"

            # Pfad zum Speichern der PDF-Datei
            file_path = os.path.join(parent_folder, pdf_file_name)

            # Artikeltext in PDF speichern
            yield scrapy.Request(full_link, callback=self.parse_article, meta={'file_path': file_path, 'category': category, 'formatted_date': formatted_date, 'index': i})
    
    # Artikel scrapen und als PDF speichern
    def parse_article(self, response):
        file_path = response.meta['file_path']
        formatted_date = response.meta['formatted_date']
        index = response.meta['index']
        category = response.meta['category']

        # Titel extrahieren
        title_parts = response.xpath('//h2/span/text()').getall()
        headline = ' '.join(title_parts) if title_parts else "No Headline"

        # Datum und Uhrzeit extrahieren
        date_time = response.xpath('//time/text()').get(default="No Date and Time")

        # Einleitung und Haupttext extrahieren
        intro = response.xpath('//header[@data-area="intro"]//p/text()').get(default="No Introduction")
        paragraphs = response.xpath('//div[@data-area="text"]//p/text()').getall()
        article_text = "\n".join(paragraphs)

        # PDF generieren und speichern
        self.generate_pdf_from_texts(headline, date_time, intro, article_text, file_path)

        print(f"Downloaded and saved as: {file_path}")
        time.sleep(5)

    # Funktion zum Filtern der Links: nur Links scrapen, die nicht in unwanted_categories sind
    # Parameter:    links - Alle Links, die auf einer Archivseite gefunden wurden
    # Rückgabe:     filtered_links - Links, die nicht zu unwanted_categories gehören
    def filter_links(self, links):
        filtered_links = []
        for link in links:
            category = link.split('/')[3]
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
            return parts[3]
        return "unknown"

    # Funktion zum Bereinigen von Sonderzeichen im Text
    def sanitize_text(self, text):
        try:
            text = text.encode('latin-1', 'replace').decode('latin-1')
        except UnicodeEncodeError as e:
            print(f"Fehler bei latin-1 Encoding: {str(e)}")
            try:
                text = text.encode('utf-8', 'ignore').decode('utf-8')
            except UnicodeEncodeError as e:
                print(f"Fehler bei utf-8 Encoding: {str(e)}")
                return text
        return text

    # PDF generieren und speichern
    def generate_pdf_from_texts(self, headline, date_time, intro, text_contents, pdf_path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        # Überschrift
        clean_headline = self.sanitize_text(headline)
        pdf.multi_cell(0, 10, txt=clean_headline, align='C')
        pdf.ln()

        # Datum und Uhrzeit
        clean_date_time = self.sanitize_text(date_time)
        pdf.multi_cell(0, 10, txt=clean_date_time)
        pdf.ln()

        # Einleitung 
        clean_intro = self.sanitize_text(intro)
        pdf.multi_cell(0, 10, txt=clean_intro)
        pdf.ln()

        # Artikelinhalt
        clean_text = self.sanitize_text(text_contents)
        pdf.multi_cell(0, 10, txt=clean_text)
        pdf.ln()

        pdf.output(pdf_path)
