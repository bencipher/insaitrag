import os
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.document_loaders import JSONLoader
import json

from mock import faq
import chromadb
from chromadb.api.types import EmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

chroma_client = chromadb.HttpClient(host="localhost", port=8019)

chroma_client.heartbeat()


def load_json_doc(filepath="faq.json"):
    loader = JSONLoader(
        file_path=filepath,
        jq_schema=".",
        text_content=False,
    )

    documents = loader.load()
    return documents


documents = load_json_doc()


def split_text():
    print(documents)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=5,
        length_function=len,
        add_start_index=True,
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks


def load_into_docs(filepath="faq.json"):
    # Load the JSON data from the file
    with open(filepath, "r", encoding="utf-8") as file:
        documents = json.load(file)

    print(documents)

    chunks = []
    for doc in documents:
        print(f"{doc=}")
        question = doc["question"]
        answers = doc["answers"]
        page_content = json.dumps({"question": question, "answers": answers})

        # Create metadata including the question and the source filename
        metadata = {
            "tag": "faq",
            "question": question,
            "answers": ", ".join(answers),
            "seq_num": 1,
            "start_index": 0,
            "source": filepath,
        }

        chunks.append(Document(metadata=metadata, page_content=page_content))

    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks


# chunks = split_text()

splitted_documents = load_into_docs()


# Define a custom embedding function wrapper
class OpenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, openai_embeddings):
        self.openai_embeddings = openai_embeddings

    def __call__(self, input):
        # Expecting input as a list of strings
        return self.openai_embeddings.embed_documents(input)


# Initialize OpenAI embeddings
openai_ef = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"))

# Create the custom embedding function
embedding_function = OpenAIEmbeddingFunction(openai_ef)


# Check if the collection already exists
collection_name = "insait"
existing_collections = chroma_client.list_collections()  # Fetch existing collections

if collection_name not in existing_collections:
    db_collection = chroma_client.create_collection(
        name=collection_name, embedding_function=embedding_function
    )
else:
    db_collection = chroma_client.get_collection(collection_name)


for doc in splitted_documents:
    if not doc.page_content:
        print(f"Skipping document with empty page_content: {doc}")
        continue

    try:
        # Access pre-built metadata directly
        question = doc.metadata["question"]
        answers = doc.metadata["answers"]
    except KeyError as e:
        print(f"Missing metadata key: {e}")
        continue

    # Check for existing documents with the same question
    existing_data = db_collection.get(where={"question": question})
    if not existing_data["documents"]:

        chunk_embedding = openai_ef.embed_documents([doc.page_content])
        doc_id = str(uuid.uuid4())
        db_collection.add(
            ids=[doc_id],
            documents=[doc.page_content],
            metadatas=[doc.metadata],
            embeddings=[chunk_embedding[0]],
        )
