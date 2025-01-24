def extract_customer_info(
    input_text: str, client, model: str, response_model
) -> CustomerDetails:
    """Extract a structured output of customer info present in input"""
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that extracts details from invoices.",
        },
        {
            "role": "user",
            "content": f"Extract customer details from {input_text}. Only return with those present in input text",
        },
    ]

    response = client.beta.chat.completions.parse(
        model=model, messages=messages, response_format=response_model
    )
    return response.choices[0].message.parsed
