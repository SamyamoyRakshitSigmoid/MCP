# Ollama Setup Guide

Quick start guide for using the Barry MCP Client with Ollama (open-source models).

## Prerequisites

### 1. Install Ollama

If you haven't already installed Ollama:

**macOS:**
```bash
brew install ollama
```

Or download from: https://ollama.ai/download

### 2. Start Ollama Server

```bash
ollama serve
```

This will start the Ollama server at `http://localhost:11434`.

### 3. Pull a Recommended Model

We recommend `llama3.1:latest` for excellent function calling support:

```bash
ollama pull llama3.1:latest
```

**Other good options:**
- `llama3.1:8b` - Meta's Llama 3.1 (good general purpose)
- `mistral:7b` - Mistral AI's model (fast and capable)
- `deepseek-coder:6.7b` - Specialized for coding tasks

To see all available models:
```bash
ollama list
```

## Installation

### 1. Install Dependencies

```bash
cd MCP\ Servers/barry-client
uv sync
```

### 2. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set:
```bash
# Ollama Configuration
OLLAMA_MODEL=llama3.1:latest
OLLAMA_BASE_URL=http://localhost:11434

# Barry Server Configuration
BARRY_SERVER_PATH=/Users/username/Documents/MCP Servers/barry-mcp-server
BARRY_SERVER_PYTHON=/Users/username/Documents/MCP Servers/barry-mcp-server/.venv/bin/python
```

## Running the Client

### Run Ollama Client

In another terminal:
```bash
cd /Users/username/Documents/MCP\ Servers/barry-client
PYTHONPATH=src .venv/bin/python -m barry_client.ollama_agent
```

## Usage Examples

Once running, try these queries:

```
You: Show me 10 chocolate products
You: Find products where fat is greater than 30
You: Give me 5 dark chocolate callets
You: What milk chocolate chips do you have?
```

## Switching Models

To use a different model:

1. Pull the model:
   ```bash
   ollama pull llama3.1:8b
   ```

2. Update `.env`:
   ```bash
   OLLAMA_MODEL=llama3.1:8b
   ```

3. Restart the client

## Troubleshooting

### "Could not connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check the URL in `.env` matches your Ollama server

### "Model not found"
- Pull the model: `ollama pull llama3.1:latest`
- Check available models: `ollama list`

### "Barry server connection failed"
- Make sure the Barry MCP server is running
- Check paths in `.env` are correct

## Advantages of Ollama

✅ **No API Key Required** - Runs completely locally  
✅ **Privacy** - Your data never leaves your machine  
✅ **Free** - No usage costs  
✅ **Fast** - Local inference, no network latency  
✅ **Flexible** - Easy to switch between models
