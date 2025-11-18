import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(prompt):
    """Call OpenRouter API with the given prompt"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        if OPENROUTER_API_KEY
        else "Bearer free-trial",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Customer Support System",
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {str(e)}"


def run_prompt_chain(customer_query):
    """
    Process a customer query through a 5-stage prompt chain.

    Args:
        customer_query (str): The customer's free-text query

    Returns:
        list: Five intermediate outputs from each stage of the chain
    """

    categories = [
        "Account Opening",
        "Billing Issue",
        "Account Access",
        "Transaction Inquiry",
        "Card Services",
        "Account Statement",
        "Loan Inquiry",
        "General Information",
    ]

    # Stage 1: Interpret the customer's intent
    stage_1_prompt = f"""Analyze the following customer query and extract their primary intent.
Query: {customer_query}
Provide a clear, concise interpretation of what the customer is asking for."""
    stage_1_output = interpret_intent(stage_1_prompt)

    # Stage 2: Map to possible categories
    stage_2_prompt = f"""Based on this intent: {stage_1_output}
Available categories: {", ".join(categories)}
Suggest 2-3 category possibilities that might apply."""
    stage_2_output = map_to_categories(stage_2_prompt)

    # Stage 3: Choose the most appropriate category
    stage_3_prompt = f"""Given these possible categories: {stage_2_output}
Original query: {customer_query}
Select the single most appropriate category."""
    stage_3_output = choose_best_category(stage_3_prompt)

    # Stage 4: Extract additional details
    stage_4_prompt = f"""For this query: {customer_query}
Category: {stage_3_output}
Identify any additional information needed (e.g., dates, amounts, account numbers, card type)."""
    stage_4_output = extract_details(stage_4_prompt)

    # Stage 5: Generate a response
    stage_5_prompt = f"""Intent: {stage_1_output}
Category: {stage_3_output}
Additional details needed: {stage_4_output}
Generate a short, helpful customer support response."""
    stage_5_output = generate_response(stage_5_prompt)

    return [
        stage_1_output,
        stage_2_output,
        stage_3_output,
        stage_4_output,
        stage_5_output,
    ]


def interpret_intent(prompt):
    """Call AI to analyze customer intent"""
    return call_openrouter(prompt)


def map_to_categories(prompt):
    """Call AI to map to categories"""
    return call_openrouter(prompt)


def choose_best_category(prompt):
    """Call AI to choose the best category"""
    return call_openrouter(prompt)


def extract_details(prompt):
    """Call AI to extract additional details"""
    return call_openrouter(prompt)


def generate_response(prompt):
    """Call AI to generate support response"""
    return call_openrouter(prompt)


def get_customer_input():
    """Collect customer query from user input"""
    print("\n" + "=" * 50)
    print("Customer Support Query System")
    print("=" * 50)
    customer_query = input("\nPlease describe your issue or question: ").strip()
    if not customer_query:
        print("Error: Please enter a valid query.")
        return get_customer_input()
    return customer_query


if __name__ == "__main__":
    query = get_customer_input()
    result = run_prompt_chain(query)
    print("\n" + "=" * 50)
    print("Support Chain Analysis Results")
    print("=" * 50)
    for i, output in enumerate(result, 1):
        print(f"\nStage {i}: {output}")
