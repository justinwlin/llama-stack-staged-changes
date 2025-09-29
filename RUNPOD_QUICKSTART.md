# RunPod Provider Quick Start

## Prerequisites
- Python 3.10+
- Git
- RunPod API token

## Setup for Development

```bash
# 1. Clone and enter the repository
cd /Users/justin/Documents/GitHub/llama-stack

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Remove any existing llama-stack installation
pip uninstall llama-stack llama-stack-client -y

# 4. Install llama-stack in development mode
pip install -e .

# 5. Build using local development code
LLAMA_STACK_DIR=. llama stack build

# When prompted during build:
# - Name: runpod-dev
# - Image type: venv
# - Inference provider: remote::runpod
# - Safety provider: IMPORTANT! Choose "llama-guard" (NOT "prompt-guard" which causes errors)
# - Other providers: accept defaults
```

**Important**: The `LLAMA_STACK_DIR=.` environment variable ensures the build uses your local development code instead of downloading from pip.

## Configure the Stack

After building, edit the generated config file:
`~/.llama/distributions/llamastack-runpod-dev/llamastack-runpod-dev-run.yaml`

### Important: Fix the Safety Provider

The build process may auto-generate a `prompt-guard` safety provider that causes errors.
**You MUST change it to `llama-guard`**:

```yaml
# Find this section and change it:
safety:
  - provider_id: llama-guard      # Changed from prompt-guard
    provider_type: inline::llama-guard  # Changed from inline::prompt-guard
    config: {}                     # Changed from config with guard_type
    module: null
```

### Add Your Models

Add your models to the `models` section using aliases for cleaner naming:

```yaml
models:
  - metadata: {}
    model_id: qwen
    model_type: llm
    provider_id: runpod
    provider_model_id: qwen/qwen3-8b

  - metadata: {}
    model_id: deepcogito
    model_type: llm
    provider_id: runpod
    provider_model_id: deepcogito/cogito-v2-preview-llama-70B
```

**Note**: Using aliases like `qwen` and `deepcogito` simplifies API calls while `provider_model_id` specifies the actual model name on RunPod.

## Run the Server

### Important: Use the Build-Created Virtual Environment

```bash
# Exit the development venv if you're in it
deactivate

# Activate the build-created venv (NOT .venv)
cd /Users/justin/Documents/GitHub/llama-stack
source llamastack-runpod-dev/bin/activate
```

### For Qwen3-8B Endpoint Self Hosted (recommended keep 1 active worker when testing)

```bash
# Set environment variables
export RUNPOD_URL="https://api.runpod.ai/v2/4xmqsuefxm31t5/openai/v1"
export RUNPOD_API_TOKEN="xxxx"

# Start server
llama stack run ~/.llama/distributions/llamastack-runpod-dev/llamastack-runpod-dev-run.yaml
```

### For DeepCogito-70B Endpoint

```bash
# Stop server (Ctrl+C) and restart with different URL
export RUNPOD_URL="https://api.runpod.ai/v2/deep-cogito-v2-llama-70b/openai/v1"
export RUNPOD_API_TOKEN="xxx"

llama stack run ~/.llama/distributions/llamastack-runpod-dev/llamastack-runpod-dev-run.yaml
```

## Test the API

### Check Available Models
```bash
curl http://localhost:8321/v1/models | python3 -m json.tool
```

### Non-streaming Request
```bash
curl -X POST http://localhost:8321/v1/inference/chat-completion \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "deepcogito",
    "messages": [{"role": "user", "content": "Hello, count to 3"}],
    "stream": false
  }'
```

### Streaming Request
```bash
curl -X POST http://localhost:8321/v1/inference/chat-completion \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "deepcogito",
    "messages": [{"role": "user", "content": "Count to 5"}],
    "stream": true
  }'
```

## Python Client Example

```python
import warnings
import logging

# Suppress warnings and httpx logs for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("httpx").setLevel(logging.WARNING)

from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:8321")

# Choose your model based on which endpoint is running:
# For Qwen3-8B (self-hosted):
MODEL_ID = "qwen"

# For DeepCogito-70B (public endpoint):
# MODEL_ID = "deepcogito"

# Non-streaming
response = client.inference.chat_completion(
    model_id=MODEL_ID,
    messages=[{"role": "user", "content": "Hello"}],
    stream=False
)
print(response.completion_message.content)

# Streaming
print("\nStreaming response:")
stream = client.inference.chat_completion(
    model_id=MODEL_ID,
    messages=[{"role": "user", "content": "Count to 3"}],
    stream=True
)

for chunk in stream:
    if hasattr(chunk, 'event'):
        if chunk.event.event_type == "progress" and chunk.event.delta:
            # Extract just the text content
            if hasattr(chunk.event.delta, 'text'):
                print(chunk.event.delta.text, end='', flush=True)

# Add newline at the end
print()
```

## Key Points

1. **Two Virtual Environments**:
   - `.venv` - Your development environment (for editing code)
   - `llamastack-runpod-dev/` - Build-created environment (for running server)
   - **Always use the build-created venv to run the server**

2. **Development Workflow**:
   - Edit code in your local repo
   - Rebuild with: `LLAMA_STACK_DIR=. llama stack build`
   - Restart server to pick up changes

3. **Model Names**: Use aliases (like `qwen`, `deepcogito`) for cleaner API calls. The provider automatically resolves aliases to the actual model names.

4. **Single Provider Limitation**: Only one RunPod URL can be active at a time. Switch between endpoints by changing RUNPOD_URL and restarting.

5. **Streaming**: RunPod requires `stream_options={"include_usage": True}` for streaming (handled automatically by the provider)

## Troubleshooting

### ModuleNotFoundError: llama_stack
- Make sure you're in the build-created venv (`llamastack-runpod-dev/`), not `.venv`
- If in `.venv`, reinstall with: `pip uninstall llama-stack -y && pip install -e .`

### Server Won't Start
- Verify RUNPOD_URL and RUNPOD_API_TOKEN are set
- Check the YAML config has correct model definitions
- Ensure you're using the build-created venv

### TypeError: ModelRegistryHelper.__init__()
- The build might have cached an old version
- Clean and rebuild:
  ```bash
  rm -rf llamastack-runpod-dev/
  rm -rf ~/.llama/distributions/llamastack-runpod-dev/
  LLAMA_STACK_DIR=. llama stack build
  ```

### Error: "not a string"
- This is usually caused by the auto-generated `prompt-guard` safety provider
- Fix by changing safety provider to `llama-guard` in the YAML config (see Configure section above)

### Streaming Not Working
- The provider automatically adds required `stream_options`
- Verify your RunPod endpoint supports streaming

## Complete Test Script

Save as `test_runpod.py`:

```python
#!/usr/bin/env python3
import os
import asyncio
from llama_stack_client import LlamaStackClient

async def test_model(client, model_id):
    """Test both streaming and non-streaming for a model"""
    print(f"\nTesting {model_id}")
    print("="*50)

    # Non-streaming test
    try:
        response = client.inference.chat_completion(
            model_id=model_id,
            messages=[{"role": "user", "content": "Count to 3"}],
            stream=False
        )
        print(f"✓ Non-streaming: {response.completion_message.content[:50]}...")
    except Exception as e:
        print(f"✗ Non-streaming failed: {e}")

    # Streaming test
    try:
        stream = client.inference.chat_completion(
            model_id=model_id,
            messages=[{"role": "user", "content": "Count to 3"}],
            stream=True
        )

        chunks = []
        for chunk in stream:
            if hasattr(chunk, 'event') and chunk.event.event_type == "progress":
                if chunk.event.delta:
                    chunks.append(chunk.event.delta)

        result = "".join(chunks)
        print(f"✓ Streaming: {result[:50]}...")
    except Exception as e:
        print(f"✗ Streaming failed: {e}")

async def main():
    print("RunPod Provider Test")
    print("="*50)
    print(f"URL: {os.getenv('RUNPOD_URL', 'Not set')}")
    print(f"Token: {'Set' if os.getenv('RUNPOD_API_TOKEN') else 'Not set'}")

    client = LlamaStackClient(base_url="http://localhost:8321")

    # Test the model matching the current RUNPOD_URL
    url = os.getenv("RUNPOD_URL", "")
    if "4xmqsuefxm31t5" in url:
        await test_model(client, "qwen")
    elif "deep-cogito" in url:
        await test_model(client, "deepcogito")
    else:
        print("Unknown endpoint URL")

if __name__ == "__main__":
    asyncio.run(main())
```

Run with: `python test_runpod.py`