# loader.py
import fitz  # PyMuPDF
import os
import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def sanitize(text: str) -> str:
    """Remove null bytes and non-printable characters at the source."""
    text = text.replace('\x00', '')
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E]', '', text)
    return text.strip()


def load_document_with_fitz(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    all_documents = []

    if ext == ".pdf":
        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text_blocks = page.get_text("blocks")

            for block in text_blocks:
                text = sanitize(block[4])  # Clean immediately after extraction
                bbox = block[:4]

                if not text:  # Skip empty blocks after cleaning
                    continue

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
