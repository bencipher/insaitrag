import pytest
from pydantic import ValidationError

from src.models import CustomerDetails


def test_normalize_communication_preference():
    # Test normalizing to lowercase for valid inputs
    customer = CustomerDetails(communication_preference="Whatsapp")
    assert customer.communication_preference == "whatsapp", "Expected 'whatsapp'"

    customer = CustomerDetails(communication_preference=" Email ")
    assert customer.communication_preference == "email", "Expected 'email'"

    customer = CustomerDetails(communication_preference="PHONE")
    assert customer.communication_preference == "phone", "Expected 'phone'"

    # Test with None, which should remain None
    customer = CustomerDetails(communication_preference=None)
    assert customer.communication_preference is None, "Expected None"

    # Test with invalid value (should raise ValidationError)
    with pytest.raises(ValidationError):
        CustomerDetails(communication_preference="sms")
