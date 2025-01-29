# chroma libs file
import os
from typing import Optional
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()
import os
from typing import Optional
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from chromadb.api.types import EmbeddingFunction

load_dotenv()


class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, fxn):
        self.embed_fxn = fxn

    def __call__(self, input):
        return self.embed_fxn.embed_documents(input)


class ChromaBaseClient:
    def __init__(
        self, collection_name: str, embedding_function: chromadb.EmbeddingFunction
    ) -> None:
        self.collection_name = collection_name
        self.embedding_function = embedding_function
        self.chroma_client = chromadb.HttpClient(
            host=os.environ.get("CHROMA_HOST"),
            port=os.environ.get("CHROMA_PORT"),
            settings=Settings(
                chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                chroma_client_auth_credentials=os.environ.get(
                    "CHROMA_AUTH_CREDENTIALS"
                ),
                chroma_auth_token_transport_header=os.environ.get(
                    "CHROMA_AUTH_TOKEN_TRANSPORT_HEADER"
                ),
            ),
        )
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        existing_collections = self.chroma_client.list_collections()
        if self.collection_name not in existing_collections:
            return self.chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
        else:
            return self.chroma_client.get_collection(self.collection_name)

    def query(self, question_embedding):
        return self.collection.query(query_embeddings=question_embedding, n_results=1)

    def add_record(
        self, ids: list, docs: list, metadatas: Optional[list], embeddings: list
    ):
        self.collection.add(
            ids=ids,
            documents=docs,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def get(self, where: dict):
        return self.collection.get(where=where)
