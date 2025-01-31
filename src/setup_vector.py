import os
import uuid
from langchain.schema import Document
import json

from dotenv import load_dotenv

from libs.chroma_db import chroma_client
from llm_models.source import ModelFactory

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

    def __init__(self, db: chroma_client.ChromaBaseClient, embedding_f):

        self.db = db
        self.embedding_fxn = embedding_f

    def embed_document(self, page_content):
        """
        Generate embeddings for a given document content.
        """
        return self.embedding_fxn.embed_documents([page_content])[
            0
        ]  # Extract first embedding

    def write_to_db(self, doc_id, doc, embedding):
        """
        Write a document and its embedding into the database.
        """
        self.db.add_record(
            ids=[doc_id],
            docs=[doc.page_content],
            metadatas=[doc.metadata],
            embeddings=[embedding],
        )

    def index_documents(self, documents):
        """
        Process and index documents into the database.
        """
        for doc in documents:
            if not doc.page_content:
                print(f"Skipping document with empty page_content: {doc}")
                continue

            try:
                question = doc.metadata["question"]
            except KeyError as e:
                print(f"Missing metadata key: {e}")
                continue

            existing_data = self.db.get(where={"question": question})
            if not existing_data["documents"]:
                embedding = self.embed_document(doc.page_content)
                doc_id = str(uuid.uuid4())
                self.write_to_db(doc_id, doc, embedding)


if __name__ == "__main__":
    provider = os.environ.get("LLM_PROVIDER").strip().lower()
    llm_model = ModelFactory().get_llm(provider)
    llm_embedding = ModelFactory().get_embedding(provider)

    document_processor = DocumentProcessor(FILE_PATH)
    documents = document_processor.load_json_doc()
    chunks = document_processor.process_documents(documents)
    embedding_fxn = chroma_client.CustomEmbeddingFunction(llm_embedding)
    chromadb_client = chroma_client.ChromaBaseClient(
        collection_name=os.environ.get("CHROMA_DB_NAME"),
        embedding_function=embedding_fxn,
    )
    embedding_indexer = EmbeddingIndexer(chromadb_client, llm_embedding)
    embedding_indexer.index_documents(chunks)
    print("Operation successful. Documents have been indexed.")
