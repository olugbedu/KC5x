import openai
import os

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"
BANNED_KEYWORDS = ["kill", "hack", "bomb"]


def is_safe(text):
    text_lower = text.lower()
    return not any(word in text_lower for word in BANNED_KEYWORDS)


def moderate_output(response):
    for word in BANNED_KEYWORDS:
        response = response.replace(word, "[REDACTED]")
    return response


def main():
    user_prompt = input("Enter your prompt: ")

    if not is_safe(user_prompt):
        print("Your input violated the moderation policy.")
        return

    system_prompt = "You are a helpful and polite assistant that provides clear, safe, and educational responses."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        output = response.choices[0].message["content"]

        if not is_safe(output):
            output = moderate_output(output)
            print("Some parts of the response were redacted for safety.")

        print("\nAI Response:\n", output)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
