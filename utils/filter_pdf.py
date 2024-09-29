import os
import shutil
import re
from PyPDF2 import PdfReader

# Ordner mit den PDFs
source_folder = 'training_set'
# Zielordner für gefundene PDFs
destination_folder = 'filtered_pdfs'

# Liste der gesuchten Wörter
search_terms = ['breitscheid', 'breitscheidplatz', 'anschlag', 'anschläge', 'weihnachtsmarkt', 'weihnachtsmärkte', 'lastwagen', 'lkw', 'terror', 'terroranschlag']

# Stelle sicher, dass der Zielordner existiert, wenn nicht, erstelle ihn
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Funktion, um den Text aus einer PDF-Datei zu extrahieren
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {pdf_path}: {e}")
    return text

# Durchsuche alle PDF-Dateien im Quellordner
for filename in os.listdir(source_folder):
    if filename.endswith('.pdf'):
        file_path = os.path.join(source_folder, filename)
        text = extract_text_from_pdf(file_path)

        # Überprüfen, ob eines der Suchwörter im Text vorkommt
        for term in search_terms:
            # Verwende reguläre Ausdrücke, um nach den Wörtern zu suchen, unabhängig von Groß-/Kleinschreibung
            if re.search(rf'\b{term}\b', text, re.IGNORECASE):
                # Datei kopieren
                shutil.copy(file_path, destination_folder)
                print(f"'{filename}' enthält '{term}' und wurde kopiert.")
                # Wenn ein Treffer gefunden wurde, hören wir auf zu suchen
                break
