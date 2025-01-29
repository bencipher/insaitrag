from models import CustomerDetails
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

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


def extract_custom_info(input_text: str, llm, response_model) -> CustomerDetails:
    """Extract a structured output of customer info present in input"""
    parser = PydanticOutputParser(pydantic_object=response_model)
    prompt = PromptTemplate(
        template="Extract customer details from the given text.\n{format_instr}\n{input_text}",
        input_variables=["input_text"],
        partial_variables={"format_instr": parser.get_format_instructions()},
    )
    ai = prompt | llm | parser
    resp = ai.invoke({"input_text": input_text})
    return resp
