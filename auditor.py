import os
import re
from langchain_groq import ChatGroq
from embedder import load_vectorstore
from prompts import COMPLIANCE_PROMPT


def sanitize(text: str) -> str:
    """Remove null bytes and non-printable characters."""
    text = text.replace('\x00', '')
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E]', '', text)
    return text


def run_audit(query: str, collection_name: str = "compliance_docs") -> str:
    vectorstore = load_vectorstore(collection_name)

    total_docs = len(vectorstore.index_to_docstore_id)
    k = min(15, max(5, total_docs // 3))
    print(f"🔍 Single Audit: {total_docs} chunks → retrieving k={k}")

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    def format_docs(docs):
        pages = set()
        texts = []
        for d in docs:
            texts.append(sanitize(d.page_content))
            pages.add(str(d.metadata.get("page", "?")))
        return "\n\n".join(texts), pages

    docs = retriever.invoke(query)
    context, pages = format_docs(docs)
    prompt_text = COMPLIANCE_PROMPT.format(context=context, question=query)
    response = llm.invoke(prompt_text)

    result = sanitize(response.content)
    return f"{result}\n\nSOURCE PAGES: {', '.join(sorted(pages))}"
