import os
from langchain_groq import ChatGroq  
from embedder import load_vectorstore
from prompts import COMPLIANCE_PROMPT

def run_audit(query: str, collection_name: str = "compliance_docs") -> str:
    vectorstore = load_vectorstore(collection_name)
    
    # Updated for FAISS: Use index_to_docstore_id to count chunks
    total_docs = len(vectorstore.index_to_docstore_id)
    
    # Calculate dynamic k (minimum 5, maximum 15)
    k = min(15, max(5, total_docs // 3))
    print(f"🔍 Single Audit: {total_docs} chunks → retrieving k={k}")
    
    # Apply the dynamic k to the retriever
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
            texts.append(d.page_content)
            pages.add(str(d.metadata.get("page", "?")))
        return "\n\n".join(texts), pages

    # The rest remains the same
    docs = retriever.invoke(query)
    context, pages = format_docs(docs)

    prompt_text = COMPLIANCE_PROMPT.format(context=context, question=query)
    response = llm.invoke(prompt_text)

    return f"{response.content}\n\nSOURCE PAGES: {', '.join(sorted(pages))}"
