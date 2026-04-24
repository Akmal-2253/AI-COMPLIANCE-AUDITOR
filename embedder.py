import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings


def clear_vectorstore():
    for key in list(st.session_state.keys()):
        if key.startswith("collection") or key == "compliance_docs":
            del st.session_state[key]


def embed_documents(chunks, collection_name="compliance_docs"):
    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    st.session_state[collection_name] = vectorstore
    return vectorstore


def load_vectorstore(collection_name="compliance_docs"):
    return st.session_state.get(collection_name)
