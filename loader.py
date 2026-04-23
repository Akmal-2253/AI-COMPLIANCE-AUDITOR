#loader.py
import fitz  # PyMuPDF
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_document_with_fitz(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    all_documents = []

    if ext == ".pdf":
        doc = fitz.open(file_path)
        # Safe way to iterate through pages
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_blocks = page.get_text("blocks") 
            for block in text_blocks:
                
                text = block[4] 
                bbox = block[:4] # (x0, y0, x1, y1)
                
                all_documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": file_path,
                        "page": page_num + 1,
                        "bbox": str(bbox) 
                    }
                ))
        doc.close()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )
    
    chunks = splitter.split_documents(all_documents)
    return chunks
