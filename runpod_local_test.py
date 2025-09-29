import warnings
import logging

# Suppress warnings and httpx logs
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("httpx").setLevel(logging.WARNING)

from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:8321")

# Non-streaming
response = client.inference.chat_completion(
    model_id="runpod/qwen/qwen3-8b",
    messages=[{"role": "user", "content": "Hello"}],
    stream=False
)
print(response.completion_message.content)

# Streaming
print("\nStreaming response:")
stream = client.inference.chat_completion(
    model_id="runpod/qwen/qwen3-8b",
    messages=[{"role": "user", "content": "Count to 3"}],
    stream=True
)

for chunk in stream:
    if hasattr(chunk, 'event'):
        if chunk.event.event_type == "progress" and chunk.event.delta:
            # Extract just the text content from the TextDelta object
            if hasattr(chunk.event.delta, 'text'):
                print(chunk.event.delta.text, end='', flush=True)

# Add newline at the end
print()