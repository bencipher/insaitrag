from typing import Optional, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from typing_extensions import Literal, TypedDict
from pydantic import BaseModel
from libs.chroma_db.chroma_client import ChromaBaseClient, CustomEmbeddingFunction


class CustomerDetails(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    communication_preference: Optional[Literal["whatsapp", "email", "phone"]] = None


class CustomerAgentDeps(BaseModel):
    existing_data: CustomerDetails = CustomerDetails()
    filepath: str
    llm: Union[ChatGoogleGenerativeAI, ChatOpenAI]
    vector_client: ChromaBaseClient
    embed_fxn: CustomEmbeddingFunction

    class Config:
        arbitrary_types_allowed = True


class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""

    role: Literal["user", "model"]
    timestamp: str
    content: str
