import os
import re
from langchain_groq import ChatGroq
from embedder import load_vectorstore, embed_documents
from loader import load_document_with_fitz
from prompts import COMPARISON_PROMPT

def load_and_embed_two_docs(path_a: str, path_b: str):
    print("📄 Embedding Doc A...")
    chunks_a = load_document_with_fitz(path_a)
    embed_documents(chunks_a, collection_name="collection_a")

    print("📄 Embedding Doc B...")
    chunks_b = load_document_with_fitz(path_b)
    embed_documents(chunks_b, collection_name="collection_b")
    print("✅ Both docs embedded.")

def extract_risk_score(report: str) -> dict:
    score = 50
    level = "MEDIUM"

    score_match = re.search(r"RISK SCORE:\s*(\d+)", report, re.IGNORECASE)
    if score_match:
        score = min(int(score_match.group(1)), 100)

    level_match = re.search(r"RISK LEVEL:\s*(HIGH|MEDIUM|LOW)", report, re.IGNORECASE)
    if level_match:
        level = level_match.group(1).upper()

    color_map = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
    return {
        "level": level,
        "score": score,
        "badge": color_map.get(level, "🟡"),
        "bar": "█" * (score // 10) + "░" * (10 - score // 10)
    }

def compare_policies(query: str) -> tuple:
    vs_a = load_vectorstore("collection_a")
    vs_b = load_vectorstore("collection_b")

    # Dynamic k for each doc separately
    total_a = vs_a._collection.count()
    total_b = vs_b._collection.count()
    k_a = min(15, max(5, total_a // 3))
    k_b = min(15, max(5, total_b // 3))
    print(f"⚖️ Doc A: {total_a} chunks → k={k_a} | Doc B: {total_b} chunks → k={k_b}")

    docs_a = vs_a.as_retriever(search_kwargs={"k": k_a}).invoke(query)
    docs_b = vs_b.as_retriever(search_kwargs={"k": k_b}).invoke(query)

    context_a = "\n\n".join([d.page_content for d in docs_a])
    context_b = "\n\n".join([d.page_content for d in docs_b])

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    prompt_text = COMPARISON_PROMPT.format(
        context_a=context_a,
        context_b=context_b,
        question=query
    )

    response = llm.invoke(prompt_text)
    report = str(response.content)
    risk = extract_risk_score(report)

    return report, risk