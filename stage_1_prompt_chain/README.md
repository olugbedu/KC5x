# Stage 1 Prompt Chain (Customer Support)

Overview
- This repository contains a small customer-support pipeline implemented in Python. The main script is:
  - stage_1_prompt_chain/prompt-chain.py
- It implements a 5-stage prompt chain that analyzes a customer's free-text query and produces a short support response.
- Each stage is implemented by sending a prompt to an AI chat model (via OpenRouter) and returning the model's text output.

Files
- prompt-chain.py — main script with the pipeline and OpenRouter integration.
- README.md — this file (explanation, usage, and notes).
- .env (optional) — environment file for OPENROUTER_API_KEY.

Requirements
- Python 3.8+
- Python packages:
  - requests
  - python-dotenv
- Install with:
  pip install requests python-dotenv

Environment variables
- OPENROUTER_API_KEY (optional): Set this in a `.env` file or environment to use your OpenRouter API key. If missing, the script uses a fallback header value intended for free/shared access.

How the code is organized and how it works
- High-level flow:
  1. The script prompts the operator for a customer query (get_customer_input()).
  2. run_prompt_chain(customer_query) constructs five prompts (one per stage).
  3. Each stage is executed by calling a helper that sends the prompt to the OpenRouter chat completions endpoint (call_openrouter).
  4. The five stage outputs are collected and printed.

- call_openrouter(prompt)
  - Purpose: send a chat-style prompt to the OpenRouter API and return the model's reply text.
  - Behavior:
    - Reads OPENROUTER_API_KEY from environment (via dotenv).
    - Builds headers:
      - Authorization: "Bearer <key>" if provided, otherwise "Bearer free-trial" fallback.
      - Content-Type: application/json
      - Additional informational headers are included in the script for traceability.
    - Builds JSON payload:
      - model: defaults to "gpt-3.5-turbo" (chosen as a free/open model in the project).
      - messages: single message with role "user" and the content equals the prompt.
      - temperature: 0.7 (controls creativity).
      - max_tokens: 300 (limits completion length).
    - Performs POST to https://openrouter.ai/api/v1/chat/completions and returns choices[0].message.content.
    - On network/API errors, returns a string describing the error (so the pipeline still returns something).

- run_prompt_chain(customer_query)
  - Purpose: orchestrate the 5-stage analysis and produce outputs for each stage.
  - Stages:
    1. Interpret intent
       - Prompt asks the model to extract the primary intent from the raw customer query.
       - Function: interpret_intent(prompt) -> delegates to call_openrouter.
    2. Map to possible categories
       - Prompt provides the interpreted intent and a fixed list of categories, asks for 2–3 candidate categories.
       - Function: map_to_categories(prompt).
    3. Choose the most appropriate category
       - Prompt provides the candidate categories and the original query, asks for a single best category.
       - Function: choose_best_category(prompt).
    4. Extract additional details
       - Prompt asks the model to list any missing details needed to resolve the request (e.g., account number, date, amount).
       - Function: extract_details(prompt).
    5. Generate a response
       - Prompt includes the intent, final category, and additional details needed, and asks the model to generate a short customer-facing response.
       - Function: generate_response(prompt).
  - Return value: a list of five strings: [stage_1_output, stage_2_output, stage_3_output, stage_4_output, stage_5_output].

- interpret_intent / map_to_categories / choose_best_category / extract_details / generate_response
  - Thin wrappers around call_openrouter that keep the code readable and allow future per-stage customization or parsing.

- get_customer_input()
  - Interactive helper that prompts the user in the terminal for a customer query. Ensures non-empty input by repeating until valid.

- Main guard (if __name__ == "__main__")
  - Collects input via get_customer_input, runs the prompt chain, then prints a labeled list of the five stage outputs.

Usage
1. Create a `.env` file in the project root (optional):
   OPENROUTER_API_KEY=your_openrouter_api_key
2. Install dependencies:
   pip install requests python-dotenv
3. Run the script:
   python KC5x/stage_1_prompt_chain/prompt-chain.py
4. Enter a customer query when prompted.

Example
- Input:
  "I can't log into my account. It says my password is wrong."
- Typical outputs (illustrative):
  - Stage 1: "User intent: regain access to account — believes password is incorrect."
  - Stage 2: "Possible categories: [Account Access, Account Opening]"
  - Stage 3: "Selected Category: Account Access"
  - Stage 4: "Additional details needed: username/email, when the issue started, any error messages"
  - Stage 5: "Short response: I'm sorry you're having trouble logging in. Please confirm the email associated with your account and any error text shown. You can reset your password using the 'Forgot password' link."

Notes and troubleshooting
- API errors: If OpenRouter is unreachable or rejects the request, call_openrouter returns the error text. Check network, endpoint, and API key validity.
- Free/shared access: Using no API key or a free key may subject the requests to rate limits or shared-instance behavior; results may vary. For production, obtain and use an API key tied to an account.
- Security: Treat OPENROUTER_API_KEY as a secret. Do not commit a `.env` containing keys into source control.
- Rate limiting and retries: The script currently does not perform automatic retries. For production use, add retry logic (exponential backoff) and error handling.
- Parsing model output: The script expects plain-text outputs. For more robust behavior, instruct the model to return JSON and parse the response to extract structured fields (e.g., category_id, required_fields, response_text).

Potential improvements
- Use structured prompts asking for JSON output to parse stage responses reliably.
- Add a caching layer to avoid repeated API calls for similar queries.
- Add authentication and logging for production deployment.
- Allow configurable model, temperature, and token limits via CLI flags or config file.
- Add unit tests and a small local mock of the OpenRouter endpoint for offline testing.

Contact / credits
- This README describes the full code flow of prompt-chain.py and how to use and extend it.
