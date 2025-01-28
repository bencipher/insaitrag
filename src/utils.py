from models import CustomerDetails


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
