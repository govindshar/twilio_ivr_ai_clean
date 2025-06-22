import os
import requests
import json

# Static key for local testing (already authorized)
GROQ_API_KEY = "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"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def ask_ai(chat_history):
    """
    Sends chat history to Groq API and retrieves the assistant's reply.

    Args:
        chat_history (list): List of message dicts in OpenAI format (role: user/assistant/system)

    Returns:
        str: Assistant reply string.
    """
    try:
        # Add system prompt if not already included
        system_prompt = {
            "role": "system",
            "content": (
                "You are a helpful health assistant. "
                "Answer user queries in 1–2 sentences. "
                "Be friendly, simple, and to the point."
            )
        }
        if not chat_history or chat_history[0].get("role") != "system":
            chat_history.insert(0, system_prompt)

        payload = {
            "model": "llama3-70b-8192",
            "messages": chat_history,
            "temperature": 0.7
        }

        print(f"\n🧠 Sending to Groq for {hash(str(chat_history)) & 0xffffffff:x}:\n", json.dumps(payload, indent=2))

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"❌ Groq API error: {response.status_code} - {response.text}")
            return "Sorry, I am having trouble processing your request."

        data = response.json()
        reply = data['choices'][0]['message']['content'].strip()
        return reply if reply else "Sorry, I couldn't find an answer."

    except Exception as e:
        print("❌ AI call failed:", e)
        return "Sorry, something went wrong. Please try again."
