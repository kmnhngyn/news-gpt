from openai import OpenAI
import gradio
import os
import config

# API key aus config-Datei setzen, damit dieser hier nicht exposed ist
os.environ["OPENAI_API_KEY"] = config.api_key

# Erstellen des OpenAI-Client-Objekts
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def query_gpt_3_5(prompt):
    # Antwort generieren über Modell 3.5, mittlerer Temperature und maximale Antwort tokens
    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=256
    )
    message = response.choices[0].message.content
    return message.strip()


def chatbot(input_text):
    response = query_gpt_3_5(input_text)
    return response


# Web-Oberfläche für Chatbot mit Gradio erstellen
chatbot_interface = gradio.Interface(
    fn=chatbot,
    inputs=gradio.Textbox(lines=5, label="Stelle eine Frage"),
    outputs="text",
    title="GPT-3.5 Plain ChatBot"
)

# Starten der Web-UI
chatbot_interface.launch(share=False)
