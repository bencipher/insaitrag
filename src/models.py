from typing import Optional, Union
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from typing_extensions import Literal, TypedDict
from pydantic import BaseModel, field_validator
from libs.chroma_db.chroma_client import ChromaBaseClient


class CustomerDetails(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    communication_preference: Optional[Literal["whatsapp", "email", "phone"]] = None

    @field_validator("communication_preference", mode="before")
    def normalize_communication_preference(cls, v):
        if isinstance(v, str):
            return v.strip().lower()  # Normalize to lowercase
        return v


class CustomerAgentDeps(BaseModel):
    existing_data: CustomerDetails = CustomerDetails()
    filepath: str
    llm: Union[ChatGoogleGenerativeAI, ChatOpenAI]
    vector_client: ChromaBaseClient
    embed_fxn: GoogleGenerativeAIEmbeddings

    class Config:
        arbitrary_types_allowed = True


class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""

    role: Literal["user", "model"]
    timestamp: str
    content: str
