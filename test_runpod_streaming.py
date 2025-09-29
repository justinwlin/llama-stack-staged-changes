#!/usr/bin/env python3
"""Test llama-stack RunPod provider streaming"""

from llama_stack_client import LlamaStackClient

# Choose your model alias:
# MODEL_ID = "qwen"
MODEL_ID = "deepcogito"

# Initialize the llama-stack client
client = LlamaStackClient(base_url="http://localhost:8321")

print(f"Testing streaming via llama-stack...")
print(f"Model: {MODEL_ID}")
print("=" * 60)

# Create a streaming chat completion request
stream = client.inference.chat_completion(
    model_id=MODEL_ID,
    messages=[
        {"role": "user", "content": "Write a short poem about stars."}
    ],
    stream=True
)

# Print the streaming response
print("Response: ", end="", flush=True)
chunk_count = 0
for chunk in stream:
    chunk_count += 1
    if hasattr(chunk, 'event'):
        if chunk.event.event_type == "progress" and chunk.event.delta:
            if hasattr(chunk.event.delta, 'text'):
                print(chunk.event.delta.text, end='', flush=True)

print(f"\n\nTotal chunks received: {chunk_count}")