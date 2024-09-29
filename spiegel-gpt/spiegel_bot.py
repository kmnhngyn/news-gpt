import config
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
import gradio

# API key aus config-Datei setzen, damit dieser hier nicht exposed ist
os.environ["OPENAI_API_KEY"] = config.api_key


# Funktion zum Erstellen eines Indexes aus den Trainingsdaten
# Dabei wird ein Vektorindex basierend auf den Dokumenten in einem Verzeichnis erstellt
# Parameter:    directory_path: Pfad zum Ordner, in dem die Trainingsdaten (Artikel) gespeichert sind
# Rückgabe:     index: erstellter Index, der später für die Antworten genutzt wird
def construct_index(directory_path):
    # Modell 3.5 mit mittlerer Temperature und maximalem output tokens
    Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.7, max_tokens=265)

    # Prüfen, ob Index bereits vorhanden
    PERSIST_DIR = "./spiegel-index/index"
    if not os.path.exists(PERSIST_DIR):
        print(f"Index neu erstellen")
        # Artikel/Dokumente aus dem gegebenen Pfad laden
        documents = SimpleDirectoryReader(directory_path).load_data()
        print(f"Es wurden {len(documents)} Dokumente geladen.")

        # Index aus Artikeln erstellen
        index = VectorStoreIndex.from_documents(documents, llm=Settings.llm)
        # Index speichern
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print(f"Index vorhanden und laden")
        # Vorhandenen Index laden
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    return index


# Funktion für den Chatbot
# Lädt den zuvor erstellten Index und verwendet ihn, um auf Eingaben des Nutzers zu antworten
# Parameter:    input_text: vom Nutzer eingegebene Frage
# Rückgabe:     response: generierte Antwort auf die Eingabe
def chatbot(input_text):
    PERSIST_DIR = "./spiegel-index/index"
    # Lade den Index aus dem gespeicherten Verzeichnis
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    query_engine = load_index_from_storage(storage_context).as_query_engine(llm=Settings.llm)

    # Im Index nach relevantem Inhalt suchen
    index_response = query_engine.query(input_text)
    relevant_content = index_response.response

    # Prompt um Antwort basierend auf Index mit GPT-3.5 zu vergleichen und zusammenzuführen
    prompt_with_context = f"Nutze diese Informationen aus spezifischen Spiegel-Artikeln: {relevant_content}. Und beantworte die folgende Frage: {input_text}"

    response = Settings.llm.complete(prompt_with_context)

    return response


# Web-Oberfläche für Chatbot mit Gradio erstellen
chatbot_interface = gradio.Interface(
    fn=chatbot,
    inputs=gradio.Textbox(lines=5, label="Stelle deine Frage"),
    outputs="text",
    title="GPT-3.5 ChatBot mit Spiegel.de-Artikeln"
)

# Path zum Ordner mit den Trainingsdaten
folder_name = 'filtered_pdfs'

# Index aus den Trainingsdaten erstellen
index = construct_index(folder_name)

# Web-Oberfläche starten
chatbot_interface.launch(share=False)
