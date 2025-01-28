import os
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.document_loaders import JSONLoader
import json
import chromadb
from chromadb.config import Settings
from chromadb.api.types import EmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

# Constants
COLLECTION_NAME = "insait2"
FILE_PATH = "faq.json"

# Initialize Chroma client
chroma_client = chromadb.HttpClient(
    host="localhost",
    port=8019,
    settings=Settings(
        chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
        chroma_client_auth_credentials=os.environ.get("CHROMA_AUTH_CREDENTIALS"),
        chroma_auth_token_transport_header=os.environ.get(
            "CHROMA_AUTH_TOKEN_TRANSPORT_HEADER"
        ),
    ),
)


class OpenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, openai_embeddings):
        self.openai_embeddings = openai_embeddings

    def __call__(self, input):
        return self.openai_embeddings.embed_documents(input)


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
    def __init__(self, collection_name, chroma_client, openai_ef):
        self.collection_name = collection_name
        self.chroma_client = chroma_client
        self.openai_ef = openai_ef

    def get_collection(self):
        existing_collections = self.chroma_client.list_collections()
        if self.collection_name not in existing_collections:
            return self.chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=OpenAIEmbeddingFunction(self.openai_ef),
            )
        else:
            return self.chroma_client.get_collection(self.collection_name)

    def index_documents(self, documents):
        db_collection = self.get_collection()
        for doc in documents:
            if not doc.page_content:
                print(f"Skipping document with empty page_content: {doc}")
                continue

            try:
                question = doc.metadata["question"]
            except KeyError as e:
                print(f"Missing metadata key: {e}")
                continue

            existing_data = db_collection.get(where={"question": question})
            if not existing_data["documents"]:
                chunk_embedding = self.openai_ef.embed_documents([doc.page_content])
                doc_id = str(uuid.uuid4())
                db_collection.add(
                    ids=[doc_id],
                    documents=[doc.page_content],
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
    embedding_indexer = EmbeddingIndexer(COLLECTION_NAME, chroma_client, openai_ef)
    embedding_indexer.index_documents(chunks)
