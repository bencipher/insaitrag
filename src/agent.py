import asyncio
import csv
from datetime import datetime, timezone
import os
from typing import Any
from openai import APIConnectionError
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from templates import system_prompt
import logfire
import chromadb
from models import ChatMessage, CustomerAgentDeps, CustomerDetails
from mock import order_statuses
from langchain_openai import OpenAIEmbeddings
from pydantic_ai import RunContext
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
import streamlit as st

logfire.configure()

logfire.info("Hello, {name}!", name="world")

load_dotenv()
model = OpenAIModel("gpt-4o", api_key=os.environ.get("OPENAI_API_KEY"))
customer_rep_agent = Agent(
    model, deps_type=CustomerAgentDeps, system_prompt=system_prompt, retries=2
)


@customer_rep_agent.tool
def retrieve_faq(ctx: RunContext[CustomerAgentDeps], question: str) -> str:
    """
    Function to retrieve answers from a predefined FAQ set.

    Args:
        question (str): The question to query the FAQ.

    Returns:
        str: The answer to the question if found, or a default message if not.

    Example Usage:
        answer = retrieve_faq("What is the return policy for items purchased at our store?")
        print(answer)"""
    print(f"In FAQ retriever: {ctx=}")
    logfire.info("Questions passed in is {question}", question=question)
    openai_ef = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"))
    question_embedding = openai_ef.embed_query(question)
    chroma_client = chromadb.HttpClient(host="localhost", port=8019)
    collection_name = "insait"
    db_collection = chroma_client.get_collection(collection_name)
    similar_documents = db_collection.query(
        query_embeddings=question_embedding, n_results=1
    )
    if similar_documents["documents"]:
        return similar_documents["documents"][0]
    else:
        return "Answer not found in the FAQ."


def is_complete(model_a: CustomerDetails, source_of_truth: CustomerDetails) -> bool:
    """
    Checks whether all fields in the CustomerDetails model are populated.

    Args:
        model_a (CustomerDetails): The current extracted details from input.
        source_of_truth (CustomerDetails): The existing state of the customer details.

    Returns:
        bool: True if the model is complete, False otherwise.
    """
    for field, value in model_a.model_dump().items():
        if value:
            setattr(source_of_truth, field, value)

    for field, value in source_of_truth.model_dump().items():
        if value is None:
            return False

    return True


@customer_rep_agent.tool
def save_customer_contact(ctx: RunContext[CustomerAgentDeps], text_input: str) -> str:
    """
    This tool connects the customer with a human customer care representative by first extracting
    customer contact information, save to CSV when complete, or indicate incomplete.
    Customer information to collect and save are: first_name, last_name, email, contact_number, address, and
    communication preference - one of "whatsapp", "email", "phone"

    Args:
        ctx (RunContext): The current agent context.
        text_input (str): The input text containing customer information.

    Returns:
        str: 'complete' if data is fully saved, 'incomplete' otherwise.
    """
    # Assuming fieldnames are defined somewhere in your code
    fieldnames = [
        "index",
        "first_name",
        "last_name",
        "email",
        "contact_number",
        "address",
        "communication_preference",
        "timestamp",
    ]

    new_extract = extract_customer_info(
        text_input, llm=ctx.deps.llm, response_model=CustomerDetails
    )

    if is_complete(new_extract, ctx.deps.existing_data):
        file_path = ctx.deps.filepath
        data = ctx.deps.existing_data.model_dump()
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not os.path.exists(file_path):
            data["index"] = 0
        else:
            with open(file_path, "r") as csvfile:
                existing_lines = csvfile.readlines()
                data["index"] = len(existing_lines)

        data["timestamp"] = current_timestamp

        ordered_data = {field: data[field] for field in fieldnames if field in data}

        with open(file_path, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not os.path.exists(file_path):
                writer.writeheader()
            writer.writerow(ordered_data)
        return "complete"
    else:
        missing_fields = [
            field for field, value in ctx.existing_data.dict().items() if value is None
        ]
        return f"incomplete: missing fields - {', '.join(missing_fields)}"


def extract_customer_info(input_text: str, llm, response_model) -> CustomerDetails:
    """Extract a structured output of customer info present in input"""
    parser = PydanticOutputParser(pydantic_object=response_model)
    prompt = PromptTemplate(
        template="Extract custoemr details from the given text.\n{format_instr}\n{input_text}",
        input_variables=["input_text"],
        partial_variables={"format_instr": parser.get_format_instructions()},
    )
    ai = prompt | llm | parser
    resp = ai.invoke({"input_text": input_text})
    return resp


@customer_rep_agent.tool
def get_order_status(ctx: RunContext[None], order_id: str) -> str:
    """
    Function to retrieve the status of an order.

    Args:
        order_id (str): The unique identifier for the order.

    Returns:
        str: A message detailing the current status of the order.

    Example Usage:
        status = get_order_status("ORD123")
        print(status)
    """
    cleaned_order_id = order_id.replace(" ", "").upper()
    if len(cleaned_order_id) != 6:
        return "Order ID is incorrect or incomplete."

    if cleaned_order_id in order_statuses:
        logfire.info("Order found")
        return order_statuses[cleaned_order_id]
    else:
        return "Order not found."


def to_chat_message(m: ModelMessage) -> ChatMessage:
    first_part = m.parts[0]
    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            return {
                "role": "user",
                "timestamp": first_part.timestamp.isoformat(),
                "content": first_part.content,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                "role": "model",
                "timestamp": m.timestamp.isoformat(),
                "content": first_part.content,
            }
    raise UnexpectedModelBehavior(f"Unexpected message type for chat app: {m}")


def run_streamlit():
    st.title("Conversational Agent")

    if "client_history" not in st.session_state:
        st.session_state.client_history = []
    if "messages" not in st.session_state:
        st.session_state.messages = []

    deps = CustomerAgentDeps(
        existing_data=CustomerDetails(),
        filepath="output.csv",
        llm=ChatOpenAI(temperature=0, model="gpt-4o"),
    )

    for message in st.session_state.client_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Ask me anything"):
        with st.chat_message("user"):
            st.markdown(user_prompt)

        if user_prompt.strip().lower() == "exit":
            st.write("Goodbye! Thanks for using the app.")
            st.stop()

        user_prompt_part = UserPromptPart(
            content=user_prompt,
            timestamp=datetime.now(timezone.utc),
            part_kind="user-prompt",
        )
        model_request = ModelRequest(parts=[user_prompt_part])
        st.session_state.messages.append(model_request)
        st.session_state.client_history.append({"role": "user", "content": user_prompt})

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:

            faq_answer = customer_rep_agent.run_sync(
                user_prompt, deps=deps, message_history=st.session_state.messages
            )
            ai_reply = faq_answer.data
        except APIConnectionError as e:
            ai_reply = f"API connection error: {e}"
            st.error(ai_reply)
        except Exception as e:
            ai_reply = f"An unexpected error occurred: {e}"
            st.error(ai_reply)
        finally:
            asyncio.set_event_loop(None)

        with st.chat_message("assistant"):
            st.markdown(ai_reply)

        st.session_state.messages.append(
            ModelResponse(
                parts=[TextPart(ai_reply)],
                timestamp=datetime.now(timezone.utc),
            )
        )
        st.session_state.client_history.append(
            {"role": "assistant", "content": ai_reply}
        )


def run_cli():
    print("AI: Hi human, I am here to help")
    all_messages = []
    deps = CustomerAgentDeps(
        existing_data=CustomerDetails(),
        filepath="output.csv",
        llm=ChatOpenAI(temperature=0, model="gpt-4o"),
    )
    while True:
        user_val = input("User: ")
        user_prompt_part = UserPromptPart(
            content=user_val,
            timestamp=datetime.now(timezone.utc),
            part_kind="user-prompt",
        )
        model_request = ModelRequest(parts=[user_prompt_part])
        all_messages.append(model_request)
        if user_val == "exit":
            print("Goodbye")
            break
        faq_answer = customer_rep_agent.run_sync(
            user_val, deps=deps, message_history=all_messages
        )
        if faq_answer._all_messages:
            last_message = faq_answer._all_messages[-1]
            if isinstance(last_message, ModelResponse):
                timestamp = last_message.timestamp
                parts = [TextPart(faq_answer.data)]
            else:
                print("The last message is not a ModelResponse.")
                timestamp = None
        else:
            print("No messages in faq_answer.")
            timestamp = None
        if timestamp is not None:
            m = ModelResponse(parts=parts, timestamp=timestamp)
            all_messages.append(m)
        print(f"AI: {faq_answer.data}")


import sys

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "cli":
            print("running CLI")
            run_cli()

    print("running browser")
    run_streamlit()
