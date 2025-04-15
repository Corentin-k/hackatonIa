
# 📄🔍 Chatbot PDF avec Azure OpenAI + Azure AI Search (RAG)

## Hackaton IA Générative - 2025 - Proposé par Microsoft et OpenCertif


Ce projet Streamlit permet d'analyser un document PDF, d'indexer son contenu dans **Azure AI Search**, et de poser des questions en langage naturel grâce à **Azure OpenAI (ChatGPT)**, le tout à l’aide de la technique RAG (Retrieval-Augmented Generation).

---

## 🧠 Objectif

Créer un chatbot capable de répondre à des questions sur le contenu d’un PDF en combinant :
- Extraction du texte des PDF,
- Génération d’**embeddings** via Azure OpenAI,
- Indexation vectorielle via **Azure AI Search**,
- Recherche vectorielle des passages pertinents,
- Génération de réponse contextuelle par un modèle GPT-4 (ou autre).

---

## ⚙️ Technologies utilisées

| Composant           | Description                                                                       |
|---------------------|-----------------------------------------------------------------------------------|
| **Streamlit**       | Frontend interactif pour uploader le PDF, poser des questions, voir les réponses. |
| **Azure OpenAI**    | Génération d’embeddings (text-embedding-ada-002) + réponse via GPT-4.             |
| **Azure AI Search** | Stockage et recherche vectorielle des segments du PDF.                            |
| **PyPDF2**          | Extraction du texte page par page dans les PDF.                                   |

---

## 📦 Dépendances Python

```bash
pip install streamlit openai azure-search-documents python-dotenv PyPDF2
```

---

## 🏗️ Ressources créées sur Azure

### 1. 🔐 Azure OpenAI

- **Ressource** : Azure OpenAI (ex: `openai-hackaton`)
- **Modèles déployés** :
  - `gpt-4o`  → pour les réponses
  - `text-embedding-ada-002` → pour les vecteurs (1536 dimensions)
- **Clés nécessaires** :
  - `AZURE_OPENAI_API_KEY`
  - `ENDPOINT_URL`

### 2. 🔎 Azure AI Search

- **Ressource** : Azure Cognitive Search (ex: `hackaton-search`)
- **Index créé** (via portail Azure de préférence) :
  - Nom : `openai_index`
  - Champs :
    - `id` : clé du document
    - `content` : contenu textuel de la page
    - `embedding` : champ vectoriel (1536 dimensions)
- **Profil vectoriel** :
  - Crée un `Vector Search Profile` appelé `default`
  - Active `HNSW` (algorithme de recherche vectorielle)
- **Clé nécessaire** :
  - `SEARCH_API_KEY`

---


## 👨‍💻 Auteur

Par Corentin KERVAGORET, Lilian CAO, Shiley MORISSEAU et Mathys BAJT
Projet développé avec l’aide de ChatGPT  

---
## 🚀 Lancer le projet

```bash
  streamlit run app.py
```


