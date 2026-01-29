# Barry MCP Client with Gemini & Ollama Integration

A remote MCP client that connects to the Barry chocolate dataset server and integrates with either **Google's Gemini API** or **Ollama (open-source models)**, allowing you to query chocolate products using natural language.

## 🎯 What This Does

- **Connects** to the Barry MCP server as a remote client
- **Integrates** with either:
  - **Gemini API** - Google's powerful cloud-based model
  - **Ollama** - Open-source models running locally (recommended!)
- **Enables** AI models to use MCP tools to query the chocolate dataset
- **Provides** an interactive chat interface

## 🚀 Quick Start

### Option 1: Ollama (Recommended - Free & Local)

See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed instructions.

```bash
# 1. Install Ollama and pull a model
ollama pull qwen2.5-coder:7b

# 2. Run the client
uv run python -m barry_client.ollama_agent
```

**Why Ollama?**
- ✅ No API key needed
- ✅ Runs completely locally (privacy!)
- ✅ Free to use
- ✅ Simpler code (~12% less than Gemini)

### Option 2: Gemini (Cloud-based)

See detailed setup below.

## 📦 Gemini Setup (Option 2)

### 1. Create Virtual Environment

```bash
cd barry-client
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -e .
```

This installs:
- `mcp` - MCP SDK for client
- `google-generativeai` - Gemini API
- `python-dotenv` - Environment variables

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```bash
# Get your API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_actual_api_key_here

# These should already be correct:
BARRY_SERVER_PATH=/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server
BARRY_SERVER_PYTHON=/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server/.venv/bin/python
```

## 🚀 Usage

### Run the Client

```bash
python -m barry_client.gemini_agent
```

Or with PYTHONPATH:

```bash
PYTHONPATH=src python src/barry_client/gemini_agent.py
```

### Example Conversation

```
🚀 Starting Barry MCP Client...
✓ Connected to Barry MCP Server
✓ Available tools: 2
  - query_skus_by_fat: Query Material_Code (SKUs) based on fat content...
  - query_chocolate_products: Search for chocolate products by type...

🤖 Initializing Gemini Agent...
✓ Initialized Gemini with 2 tools

============================================================
Barry MCP Client with Gemini - Ready!
============================================================

You can now ask questions about chocolate products.
Examples:
  - Show me 10 products where fat is greater than 30
  - Give me 5 dark chocolate callets
  - Find milk chocolate chips

Type 'quit' or 'exit' to stop.

You: Show me 5 dark chocolate callets

💬 You: Show me 5 dark chocolate callets

🔧 Gemini calling tool: query_chocolate_products
   Arguments: {'chocolate_type': 'Dark', 'moulding_type': 'callets', 'n': 5}
✓ Tool result received (1234 chars)

🤖 Gemini: Here are 5 dark chocolate callets from the Barry dataset:

1. **CHD-12345** - Dark Chocolate Callets 70%
   - Fat: 35.2g
   - Description: Premium dark chocolate callets with 70% cocoa content...

2. **CHD-67890** - Organic Dark Callets
   - Fat: 33.1g
   - Description: Certified organic dark chocolate callets...

[... more results ...]
```

## 🔧 How It Works

### Architecture

```
User Query
    ↓
Gemini API (natural language understanding)
    ↓
Gemini decides to use MCP tools
    ↓
MCP Client (connects to Barry server via stdio)
    ↓
Barry Server (queries chocolate dataset)
    ↓
Results flow back through MCP Client
    ↓
Gemini formats and presents results
    ↓
User sees formatted response
```

### Components

1. **client.py** - MCP client that connects to Barry server
   - Manages stdio connection
   - Lists available tools
   - Executes tool calls
   - Converts tool schemas for Gemini

2. **gemini_agent.py** - Gemini integration
   - Initializes Gemini with MCP tools
   - Handles conversation loop
   - Manages function calling
   - Formats responses

## 📝 Available Tools

### 1. query_skus_by_fat

Query products by fat content using comparison operators.

**Parameters:**
- `fat_value` (required): Fat threshold in grams
- `operator` (optional): Comparison operator (==, <, <=, >, >=), default: ">"
- `n` (optional): Number of results, default: 10

**Example queries:**
- "Show me products with fat greater than 30 grams"
- "Find 5 SKUs where fat is less than 15"

### 2. query_chocolate_products

Search for chocolate products by type and moulding.

**Parameters:**
- `chocolate_type` (required): Dark, Milk, or White
- `moulding_type` (required): e.g., "callets", "chips", "blocks"
- `n` (optional): Number of results, default: 5

**Example queries:**
- "Give me dark chocolate callets"
- "Find 10 milk chocolate chips"
- "Show me white chocolate blocks"

## 🛠️ Troubleshooting

### "GEMINI_API_KEY not set"

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and add it to `.env`.

### "Cannot connect to Barry server"

Make sure:
1. Barry server path is correct in `.env`
2. Barry server's venv Python path is correct
3. Barry server dependencies are installed

### "Tool call failed"

Check that:
1. Barry server is working: `cd ../barry-mcp-server && PYTHONPATH=src .venv/bin/python -m barry_server.server`
2. Dataset file exists in `barry-mcp-server/data/`

## 🎓 Learning Points

This project demonstrates:
- **MCP Client Implementation** - How to connect to MCP servers remotely
- **Gemini Function Calling** - Integrating LLM with external tools
- **Async Python** - Using asyncio for concurrent operations
- **stdio Communication** - Process-to-process communication
- **Tool Schema Conversion** - Adapting MCP tools for Gemini

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## 🔑 Key Features

✅ **Natural Language Queries** - Ask questions in plain English  
✅ **Automatic Tool Selection** - Gemini chooses the right tool  
✅ **Function Calling** - Seamless MCP tool integration  
✅ **Interactive Chat** - Conversational interface  
✅ **Error Handling** - Graceful error management  
✅ **Rich Formatting** - Emoji indicators and structured output  

---

**Version:** 0.1.0  
**Status:** Ready to use! 🎉
