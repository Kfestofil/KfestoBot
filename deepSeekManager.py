import subprocess
import requests
import asyncio
import aiohttp
from collections import defaultdict

import re

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"


class DeepSeekSession:
    def __init__(self, ai_name="Kfestobot"):
        self.ai_name = ai_name
        self.system_prompt = ""
        self.message_histories = defaultdict(list)  # Stores all message histories in session

    def set_system_prompt(self, prompt: str):
        """Sets the system prompt for guiding the AI."""
        self.system_prompt = prompt

    def append_message(self, author: str, message: str, channel_id):
        self.message_histories[channel_id].append({"user": author, "content": message})
        if len(self.message_histories[channel_id]) > 50:
            self.message_histories[channel_id].pop(0)

    async def generate_response(self, channel_id):
        """Sends the conversation to DeepSeek and returns the AI's response."""
        if not await is_ollama_running():
            return "Error: Ollama is not running."

        # Combine the messages into a conversation-like format
        combined_message = f"Here is the conversation so far, write your ({self.ai_name}'s) next response:\n\n"
        combined_message += "\n\n".join([f"({msg['user']}): {msg['content']}" for msg in self.message_histories.get(channel_id)])
        combined_message += f"\n\nDo not add '({self.ai_name}):' or quote marks, or anything similar at the start!"

        # Send the system prompt and combined conversation as a single message to the AI
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": self.system_prompt},  # Keep the system prompt as is
                {"role": "user", "content": combined_message}  # Combined conversation history
            ],
            "stream": False
        }
        # print(data)
        print(combined_message)
        # print(self.message_histories)
        response = requests.post(OLLAMA_URL, json=data)
        ai_message = response.json().get("message", {}).get("content", "Error: No response.")

        return ai_message

    # async def generate_response(self):
    #     """Sends the conversation to DeepSeek and returns the AI's response asynchronously."""
    #     if not await is_ollama_running():
    #         print("Ollama not running or timed out")
    #         return "Error: Ollama is not running."
    #
    #     data = {
    #         "model": MODEL_NAME,
    #         "messages": [{"role": "system", "content": self.system_prompt}] + self.message_history,
    #         "stream": False
    #     }
    #
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(OLLAMA_URL, json=data) as response:
    #             response_json = await response.json()
    #             ai_message = response_json.get("message", {}).get("content", "Error: No response.")
    #
    #     # Clean AI response
    #     ai_message = re.sub(r'<think>.*?</think>', '', ai_message, flags=re.DOTALL).strip()
    #
    #     return ai_message

    def reset_session(self):
        """Clears the message history while keeping the system prompt."""
        self.message_history = []


async def is_ollama_running():
    """Checks if Ollama is running by querying the available models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


async def start_ollama():
    """Starts the Ollama server if it's not already running."""
    if await is_ollama_running():
        return True  # Already running
    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(["ollama", "run", MODEL_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait until Ollama is running
    for _ in range(10):  # Retry for a few seconds
        if await is_ollama_running():
            return True
        await asyncio.sleep(1)

    return False

def stop_ollama():
    """Stops the Ollama process."""
    subprocess.run(["taskkill", "/F", "/IM", "ollama*"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

