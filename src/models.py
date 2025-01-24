from typing import Optional
from langchain_openai import ChatOpenAI
from typing_extensions import Literal, TypedDict
from pydantic import BaseModel
from openai import OpenAI


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
    llm: ChatOpenAI

    class Config:
        arbitrary_types_allowed = True


class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""

    role: Literal["user", "model"]
    timestamp: str
    content: str
