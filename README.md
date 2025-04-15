# 📄🔍 LegalHelp AI – Chatbot d’Assistance Juridique pour Salariés

### 🧠 Projet développé dans le cadre du Hackathon IA Générative 2025  
📍 Organisé par **Efrei**, **Microsoft** et **OpenCertif**

---

## 🎯 Objectifs du Projet

**LegalHelp AI** est un assistant virtuel conçu pour accompagner les salariés confrontés à des situations juridiques au travail. Grâce à l’IA générative, il leur permet de :

- Identifier rapidement les situations potentiellement litigieuses.
- Recevoir des conseils concrets et structurés, étape par étape.
- Savoir quelles preuves rassembler (guides, fiches pratiques, modèles de lettres, témoignages…).
- Comprendre les démarches à entreprendre en cas d’abus professionnel.

> 💡 L'objectif : démocratiser l'accès à une première orientation juridique claire et immédiate.

---

## 🛠️ Stack Technique & Fonctionnalités

Le projet repose sur une architecture moderne combinant extraction de documents, recherche vectorielle et génération de texte augmentée (RAG).

| Composant           | Rôle                                                                 |
|---------------------|----------------------------------------------------------------------|
| **Streamlit**       | Interface web interactive (upload de PDF, Q&A en langage naturel).   |
| **Azure OpenAI**    | Embedding des textes & génération des réponses (GPT-4o).             |
| **Azure AI Search** | Indexation & recherche vectorielle des documents.                    |
| **PyPDF2**          | Extraction du contenu textuel page par page à partir des PDF.        |

---

## 📦 Installation des Dépendances

```bash
pip install streamlit openai azure-search-documents python-dotenv PyPDF2
```

---

## 🏗️ Infrastructure Azure

### 🔐 1. Azure OpenAI

- **Ressource** : `openai-hackaton`
- **Modèles utilisés** :
  - `gpt-4o` → génération de réponses
  - `text-embedding-ada-002` → création de vecteurs (1536 dimensions)
- **Variables d’environnement nécessaires** :
  - `AZURE_OPENAI_API_KEY`
  - `ENDPOINT_URL`

### 🔎 2. Azure AI Search

- **Ressource** : `hackaton-search`
- **Index à créer** :
  - **Nom** : `openai_index`
  - **Champs** :
    - `id` : identifiant unique
    - `content` : contenu textuel du document
    - `embedding` : vecteurs d’embedding (1536 dimensions)
- **Configuration vectorielle** :
  - Créer un profil `Vector Search Profile` appelé `default`
  - Activer l’algorithme **HNSW** (recherche vectorielle haute performance)
- **Clé API requise** :
  - `SEARCH_API_KEY`

---

## 🚀 Lancer l’application

```bash
streamlit run app.py
```

---

## 👥 Équipe projet

Développé par :
- **Corentin KERVAGORET**
- **Lilian CAO**
- **Shiley MORISSEAU**
- **Mathys BAJT**  
Avec le soutien de **ChatGPT** 🤖

---

## 🔗 Liens utiles

- [📘 Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [🔎 Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [📄 Streamlit Docs](https://docs.streamlit.io/)
- [📚 PyPDF2 Documentation](https://pypi.org/project/PyPDF2/)
- [📦 azure-search-documents (Python)](https://pypi.org/project/azure-search-documents/)

---