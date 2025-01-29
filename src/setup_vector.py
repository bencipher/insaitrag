import os
import uuid
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import json

from dotenv import load_dotenv

from libs.chroma_db import chroma_client

load_dotenv()

# Constants
FILE_PATH = "faq.json"


# class to manage documents loading and processing
class DocumentProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_json_doc(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            documents = json.load(file)
            return documents

    def process_documents(self, documents):
        chunks = []
        for doc in documents:
            question = doc["question"]
            answers = doc["answers"]
            page_content = json.dumps({"question": question, "answers": answers})

            metadata = {
                "tag": "faq",
                "question": question,
                "answers": ", ".join(answers),
                "seq_num": 1,
                "start_index": 0,
                "source": self.file_path,
            }

            chunks.append(Document(metadata=metadata, page_content=page_content))
        return chunks


# Class to handle embedding and indexing
class EmbeddingIndexer:

    def __init__(self, chroma_client: chroma_client.ChromaBaseClient, embedding_f):

        self.chroma_client = chroma_client
        self.embedding_fxn = embedding_f

    def index_documents(self, documents):
        for doc in documents:
            if not doc.page_content:
                print(f"Skipping document with empty page_content: {doc}")
                continue

            try:
                question = doc.metadata["question"]
            except KeyError as e:
                print(f"Missing metadata key: {e}")
                continue

            existing_data = self.chroma_client.get(where={"question": question})
            if not existing_data["documents"]:
                chunk_embedding = self.embedding_fxn.embed_documents([doc.page_content])
                doc_id = str(uuid.uuid4())
                self.chroma_client.add_record(
                    ids=[doc_id],
                    docs=[doc.page_content],
                    metadatas=[doc.metadata],
                    embeddings=[chunk_embedding[0]],
                )


if __name__ == "__main__":
    # Process documents and index them
    document_processor = DocumentProcessor(FILE_PATH)
    documents = document_processor.load_json_doc()
    print(f"{documents=}")
    chunks = document_processor.process_documents(documents)
    
    openai_ef = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"))
    embedding_fxn = chroma_client.CustomEmbeddingFunction(openai_ef)
    chromadb_client = chroma_client.ChromaBaseClient(
        collection_name=os.environ.get("CHROMA_DB_NAME"),
        embedding_function=embedding_fxn,
    )
    embedding_indexer = EmbeddingIndexer(chromadb_client, openai_ef)
    embedding_indexer.index_documents(chunks)
    print("Operation successful. Documents have been indexed.")
