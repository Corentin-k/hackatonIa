import os

import streamlit as st
import PyPDF2
from docx import Document
from textwrap import wrap
import re

# Azure
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
load_dotenv()


# --------------------------
# Style personnalisé
# --------------------------
MAIN_COLOR = "#304FFE"
BACKGROUND_COLOR = "#F8F9FA"
TEXT_COLOR = "#212121"
ALERT_COLOR = "#E3F2FD"

custom_css = f"""
<style>
    /* Configuration générale */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}

    /* En-tête */
    h1 {{
        color: {MAIN_COLOR} !important;
        margin-bottom: 0.2rem !important;
    }}

    h3 {{
        color: {TEXT_COLOR} !important;
        margin-bottom: 2rem !important;
    }}

    /* Widgets */
    .stTextArea>div>div>textarea, 
    .stFileUploader>div>div {{
        border: 1px solid {MAIN_COLOR} !important;
    }}

    .stButton>button {{
        background-color: {MAIN_COLOR} !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }}

    .stButton>button:hover {{
        opacity: 0.9;
        transform: scale(1.02);
    }}

    /* Alertes */
    .stAlert {{
        background-color: {ALERT_COLOR} !important;
        border-left: 4px solid {MAIN_COLOR} !important;
    }}

    /* Footer */
    .footer {{
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 1rem;
        color: {MAIN_COLOR} !important;
        font-size: 0.8rem;
    }}

    /* Nouveaux styles */
    .stInfo {{
        border-left: 4px solid {MAIN_COLOR} !important;
        padding-left: 1rem !important;
    }}

    .stSuccess {{
        background-color: {ALERT_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    .document-match {{
        background-color: #E8F5E9 !important;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
</style>
"""

# --------------------------
# Configuration Streamlit
# --------------------------
st.set_page_config(
    page_title="LegalHelp AI",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>LegalHelp AI ⚖️</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Votre espace confidentiel d'accompagnement</h3>", unsafe_allow_html=True)

# --------------------------
# Configuration Azure OpenAI
# --------------------------
endpoint = os.getenv("ENDPOINT_URL")
deployment_chat = os.getenv("DEPLOYMENT_NAME")
deployment_embedding = os.getenv("DEPLOYMENT_EMBEDDING")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    azure_endpoint=endpoint, # URL du service Azure OpenAI
    api_key=subscription_key, # Clé d'accès au service Azure OpenAI
    api_version="2024-05-01-preview", # Version de l'API
)

# --------------------------
# Configuration Azure AI Search
# --------------------------
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_api_key = os.getenv("SEARCH_API_KEY")
index_name = os.getenv("SEARCH_INDEX_NAME")

search_client = SearchClient(
    endpoint=search_endpoint, # URL du service Azure Search
    index_name=index_name, # Nom de l'index
    credential=AzureKeyCredential(search_api_key) # Clé d'accès au service Azure Search
)


# --------------------------
# Fonctions principales
# --------------------------

def get_embedding(text):
    """
    Fonction pour générer un embedding à partir d'un texte donné : transforme le texte en vecteur
    :param text: Texte à transformer en embedding
    :return: Vecteur d'embedding
    """
    try:
        with st.spinner("Génération de l'embedding..."):
            embedding_response = client.embeddings.create( # Création de l'embedding permet de transformer le texte en vecteur
                model=deployment_embedding, # Modeèle d'OpenAI
                input=text # Texte à transformer
            )
            return embedding_response.data[0].embedding
    except Exception as e:
        st.error(f"Erreur lors de la génération de l'embedding : {e}")
        return None


def index_document(documents):
    """
    Fonction pour indexer un document dans Azure Search
    :param documents: Liste de documents à indexer
    :return:
    """
    try:
        for doc in documents:
            doc["@search.action"] = "upload"
        search_client.upload_documents(documents=documents)
        st.success("Indexation effectuée.")
    except Exception as e:
        st.error(f"Erreur lors de l'indexation : {e}")


def search_vector(query_embedding):
    """
    Fonction pour effectuer une recherche vectorielle dans Azure Search
    :param query_embedding:  Vecteur de la requête
    :return:
    """
    try:
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=5,
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


def split_text(text, max_len=1000):
    return wrap(text, max_len)


def extract_text_from_file(file):
    """
    Fonction pour extraire le texte d'un fichier
    :param file:
    :return:
    """
    if file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf_reader.pages])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        st.warning("Format non supporté")
        return None


# --------------------------
# Interface utilisateur
# --------------------------
st.subheader("📁 Téléversement d’un document juridique")
document_file = st.file_uploader("Téléchargez votre document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if document_file:
    try:
        document_text = extract_text_from_file(document_file)
        if document_text:
            st.write(f"Texte extrait ({len(document_text)} caractères)")
            segments = []
            chunks = split_text(document_text)
            safe_filename = re.sub(r'[^a-zA-Z0-9_\-=]', '_', document_file.name)

            for idx, chunk in enumerate(chunks):
                embedding = get_embedding(chunk)
                if embedding:
                    segments.append({
                        "id": f"{safe_filename}_chunk_{idx + 1}",
                        "content": chunk,
                        "embedding": embedding,
                        "filename": document_file.name,
                        "chunk_number": idx + 1
                    })

            if segments:
                index_document(segments)
            else:
                st.warning("Aucun contenu pertinent détecté")
        else:
            st.warning("Erreur d'extraction du texte")
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")

st.subheader("📝 Décrivez votre situation")
user_question = st.text_area("Expliquez votre situation :")

if st.button("Analyser ma situation"):
    if user_question:
        st.info("Analyse en cours...")
        query_embedding = get_embedding(user_question)
        document_context = ""
        used_chunks = []

        if query_embedding:
            results = search_vector(query_embedding)

            if results:
                with st.expander("📑 Extraits juridiques utilisés", expanded=True):
                    for i, result in enumerate(results, 1):
                        st.markdown(f"**Extrait #{i}** (source: {result['filename']})")
                        st.caption(f"Segment {result['chunk_number']}")
                        st.info(result['content'][:500] + "...")
                        st.divider()
                        used_chunks.append(result['content'])
                        document_context += f"\n- {result['content']}\n"

                st.success(f"📚 {len(results)} extraits pertinents trouvés")
            else:
                document_context = "Aucun extrait pertinent trouvé"
                st.info("ℹ️ Analyse basée sur les connaissances générales")

        prompt_context = f"""
            CONTEXTE DOCUMENTAIRE:
            {document_context}

            QUESTION UTILISATEUR:
            {user_question}

            INSTRUCTIONS:
            - Répondre en français
            - Citer les sources documentaires utilisées
            - Mentionner les noms des documents référencés
            - Ton professionnel et accessible
        """

        messages = [
            {"role": "system", "content": "Assistant juridique spécialisé en droit du travail français."},
            {"role": "user", "content": prompt_context}
        ]

        try:
            completion = client.chat.completions.create(
                model=deployment_chat,
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )

            reply = completion.choices[0].message.content
            st.markdown("### Résultat de l’analyse :")
            st.write(reply)

            st.markdown("---")
            with st.expander("🔍 Détails techniques"):
                st.write(
                    f"**Documents utilisés:** {', '.join(set(r['filename'] for r in results)) if results else 'Aucun'}"
                )
                st.write(f"**Extraits pertinents:** {len(results) if results else 0}")

                st.write(f"**Modèle IA:** {deployment_chat}")

            st.warning("⚠️ Conseil informatif - Consultez un avocat pour une analyse personnalisée")

        except Exception as e:
            st.error(f"Erreur de génération : {e}")
    else:
        st.warning("Veuillez décrire votre situation")

# ========== Footer ==========
st.markdown(f"""
<div class='footer'>
    LegalHelp AI © 2025 — Mentions légales | Confidentialité | Contact
</div>
""", unsafe_allow_html=True)