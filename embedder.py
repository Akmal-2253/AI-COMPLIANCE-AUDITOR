# embedder.py
import os
import shutil
import gc
import random
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "vectorstore"

# Remove @st.cache_resource — just use a global variable instead
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("⏳ Loading HuggingFace Embeddings Model (First time only)...")
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings

def clear_vectorstore():
    if os.path.exists(CHROMA_PATH):
        gc.collect()
        try:
            shutil.rmtree(CHROMA_PATH, ignore_errors=True)
        except Exception:
            new_name = f"old_store_{random.randint(1, 999)}"
            os.rename(CHROMA_PATH, new_name)

def embed_documents(chunks, collection_name="compliance_docs"):
    embeddings = get_embeddings()
    try:
        existing = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        existing.delete_collection()
    except:
        pass

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=collection_name
    )
    print(f"✅ Embedded {len(chunks)} chunks into '{collection_name}'")
    return vectorstore

def load_vectorstore(collection_name="compliance_docs"):
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=collection_name
    )