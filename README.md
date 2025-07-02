# Nyaay-buddy ⚖️
# Legal Judgement NER and RAG-Based Question Answering System

This project focuses on simplifying access to legal information for non-experts. It uses a fine-tuned BERT model to extract named entities from Indian legal judgment documents and integrates a Retrieval-Augmented Generation (RAG) pipeline to answer user queries based on those documents. The system is deployed through a FastAPI backend and is accessible via a lightweight web interface.

---

## Project Overview

- **NER Model**: Fine-tuned `bert-base-cased` using Hugging Face Transformers on Indian court judgments.
- **Question Answering**: Implemented a RAG pipeline to answer user queries based on context retrieved from judgment documents.
- **Deployment**: Backend developed using FastAPI, served to a frontend via REST APIs.
- **Frontend**: HTML/CSS interface built by team members.
- **Additional Integrations**: Gemini API used by teammates to provide question-answering over legal cases; an additional model was fine-tuned for preambles of court hearings.

---

## Demonstration Video

Watch a walkthrough of the system here:  
📺 [YouTube Demo Link](https://youtu.be/2F8Kdta1zc0)

---

## Dataset

- **Source**: [Legal-NLP-EkStep/legal_NER](https://github.com/Legal-NLP-EkStep/legal_NER)
- **Size**: ~9,435 annotated samples
- **Annotation Format**: BIO tagging scheme
- **Entities Covered**: `CASE_NUMBER`, `COURT`, `JUDGE`, `DATE`, `PETITIONER`, `RESPONDENT`, `STATUTE`, `PROVISION`, `GPE`, `ORG`, `OTHER_PERSON`, `WITNESS`, `PRECEDENT`.

---

## Model Performance

Training Summary:
- **Epochs**: 3  
- **Evaluation Loss**: 0.1997  
- **Accuracy**: ~94.15%  
- **Macro F1-Score**: ~0.51  
- **Weighted F1-Score**: ~0.93  

Entity-wise performance varied due to class imbalance in the dataset. Entities such as `B-DATE`, `I-PRECEDENT`, and `I-PROVISION` showed high performance, while labels like `B-JUDGE`, `B-ORG`, and `B-WITNESS` were underrepresented.

---


---

## Roles & Contributions

### My Contributions (Ravikant Saraf)
- Fine-tuned BERT on Indian legal judgment documents for NER.
- Developed a Retrieval-Augmented Generation (RAG) chatbot using LangChain and Hugging Face models for judgment-based legal question answering.
- Built and deployed the backend using FastAPI.

### Team Contributions
- Designed and built the HTML/CSS frontend.
- Integrated Gemini API for QA on general legal case queries.
- Fine-tuned an additional model on court preamble documents.

---

## Tech Stack

- Python
- Hugging Face Transformers
- PyTorch
- LangChain (for RAG)
- FastAPI
- HTML/CSS (Frontend by team)
- Gemini API (integrated by teammates)

---

## Future Enhancements

- Expand annotated dataset with more balanced entity distribution.
- Add Streamlit or Hugging Face Space for simplified public demo.
- Improve performance on low-frequency labels via active learning or class weighting.
- Add multilingual support for regional legal texts.

---





