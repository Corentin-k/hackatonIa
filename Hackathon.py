import os
import json
import streamlit as st
import PyPDF2
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

# --------------------------
# Chargement des variables d'environnement
# --------------------------
load_dotenv()

# --------------------------
# Configuration Streamlit
# --------------------------
st.set_page_config(page_title="Chatbot + Analyse PDF", page_icon=":robot_face:")
st.title("Chatbot Azure OpenAI et Azure AI Search avec Analyse PDF")
st.write("Téléchargez un PDF, indexez-le, posez une question et obtenez une réponse enrichie par le contenu du document.")

# --------------------------
# Configuration Azure OpenAI
# --------------------------
endpoint = os.getenv("ENDPOINT_URL", "https://openia-hackaton.openai.azure.com/")
deployment_chat = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
deployment_embedding = os.getenv("DEPLOYMENT_EMBEDDING", "text-embedding-ada-002")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)

# --------------------------
# Configuration Azure AI Search (index déjà créé)
# --------------------------
search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://hackaton-search.search.windows.net")
search_api_key = os.getenv("SEARCH_API_KEY")
index_name = os.getenv("SEARCH_INDEX_NAME", "openai_index")

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_api_key)
)

# --------------------------
# Fonction pour générer un embedding
# --------------------------
def get_embedding(text):
    try:
        with st.spinner("Génération de l'embedding..."):
            embedding_response = client.embeddings.create(
                model=deployment_embedding,
                input=text
            )
            return embedding_response.data[0].embedding
    except Exception as e:
        st.error(f"Erreur lors de la génération de l'embedding : {e}")
        return None

# --------------------------
# Fonction d'indexation (envoi dans l'index Azure)
# --------------------------
def index_document(documents):
    try:
        for doc in documents:
            doc["@search.action"] = "upload"
        result = search_client.upload_documents(documents=documents)
        st.success("Indexation effectuée.")
    except Exception as e:
        st.error(f"Erreur lors de l'indexation : {e}")

# --------------------------
# Fonction de recherche vectorielle
# --------------------------
def search_vector(query_embedding, top=5):
    try:
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top,
            fields="embedding"
        )
        results = search_client.search(
            search_text="",
            vector_queries=[vector_query]
        )
        return list(results)
    except Exception as e:
        st.error(f"Erreur lors de la recherche vectorielle : {e}")
        return []

# --------------------------
# Extraction PDF + indexation
# --------------------------
pdf_file = st.file_uploader("Téléchargez votre PDF", type=["pdf"])
if pdf_file:
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        segments = []
        st.write(f"Nombre de pages détectées : {len(pdf_reader.pages)}")
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip() != "":
                st.write(f"Extrait page {i+1} (200 premiers caractères) :")
                st.write(page_text[:200] + "...")
                embedding = get_embedding(page_text)
                if embedding:
                    segments.append({
                        "id": f"page_{i+1}",
                        "content": page_text,
                        "embedding": embedding
                    })
        if segments:
            index_document(segments)
        else:
            st.warning("Aucun contenu pertinent détecté dans ce PDF.")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF : {e}")

# --------------------------
# Interface de question
# --------------------------
user_question = st.chat_input("Posez une question à propos du PDF")

if user_question:
    query_embedding = get_embedding(user_question)
    pdf_context = ""
    if query_embedding:
        results = search_vector(query_embedding)
        if results:
            st.markdown("### Résultats de la recherche vectorielle :")
            for idx, doc in enumerate(results):
                st.write(f"**Résultat {idx+1}**")
                content = doc.get("content", "Aucun contenu trouvé")
                st.write(content)
                pdf_context += "\n" + content
                st.write("---")
        else:
            st.info("Aucun résultat trouvé dans l'index.")

    prompt_context = ("Contexte provenant du PDF :\n" + pdf_context +
                      "\n\nQuestion de l'utilisateur : " + user_question)
    messages = [
        {"role": "system", "content": "Tu es un assistant qui répond en te basant sur le contenu d'un PDF."},
        {"role": "user", "content": prompt_context}
    ]
    try:
        completion = client.chat.completions.create(
            model=deployment_chat,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )
        st.expander("Voir la réponse brute du chat").write(json.loads(completion.model_dump_json()))
        reply = completion.choices[0].message.content
        st.markdown("### Réponse du Chat :")
        st.write(reply)
    except Exception as e:
        st.error(f"Erreur lors de la génération du chat : {e}")


