# Barry MCP Client - Complete Codebase Walkthrough

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Core Components Deep Dive](#core-components-deep-dive)
5. [Data Flow](#data-flow)
6. [Setup & Usage](#setup--usage)
7. [How Everything Works Together](#how-everything-works-together)

---

## 🎯 Project Overview

**Barry MCP Client** is a remote client that connects to the Barry MCP server and integrates with Google's Gemini API, enabling natural language queries about chocolate products through Gemini's function calling capabilities.

**What it does:**
- Connects to Barry MCP server (chocolate dataset with 44,538 unique SKUs)
- Integrates with Gemini API for natural language understanding
- Enables Gemini to call MCP tools to query chocolate products
- Provides an interactive terminal chat interface

**Key Achievement:** Successfully bridges MCP protocol with Gemini's function calling, allowing Gemini to query a local dataset through MCP tools.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Terminal                            │
│              (Interactive Chat Interface)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ User Query: "Give me 5 dark chocolate callets"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Gemini API (google-genai)                  │
│  - Natural language understanding                           │
│  - Decides to use query_chocolate_products tool             │
│  - Formats final response                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Function Call: query_chocolate_products(...)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Barry MCP Client (client.py)                   │
│  - Manages MCP session                                      │
│  - Converts tool schemas for Gemini                         │
│  - Executes tool calls on Barry server                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ stdio (stdin/stdout) subprocess
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Barry MCP Server (server.py)                   │
│  - Loads 195MB chocolate dataset                            │
│  - Deduplicates to 44,538 unique SKUs                       │
│  - Queries pandas DataFrame                                 │
│  - Returns formatted results                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
barry-client/
├── src/
│   └── barry_client/
│       ├── __init__.py          # Package initialization (4 lines)
│       ├── client.py            # MCP client (138 lines)
│       └── gemini_agent.py      # Gemini integration (203 lines)
├── .venv/                       # Virtual environment
├── .env                         # API keys (user-created)
├── .env.example                 # API key template
├── .gitignore                   # Git ignore rules
├── pyproject.toml               # Project configuration
└── README.md                    # User documentation
```

**Total Code:** ~345 lines of Python

---

## 🔧 Core Components Deep Dive

### 1. **pyproject.toml** - Project Configuration

```toml
[project]
name = "barry-client"
version = "0.1.0"
description = "Remote MCP client for Barry server with Gemini integration"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.9.0",           # MCP SDK for client
    "google-genai>=0.1.0",  # New Gemini API
    "python-dotenv>=1.0.0", # Environment variables
]
```

**Key Points:**
- Uses new `google-genai` package (not deprecated `google-generativeai`)
- Requires Python 3.10+ for modern type hints
- Minimal dependencies (only 3 direct deps)

---

### 2. **client.py** - MCP Client Implementation

#### **Class: BarryMCPClient**

**Purpose:** Manages connection to Barry MCP server and tool execution

**Key Methods:**

##### `__init__(server_path, server_python)`
```python
def __init__(self, server_path: str, server_python: str):
    self.server_path = Path(server_path)
    self.server_python = server_python
    self.session: ClientSession | None = None
    self.tools = []
```
- Stores server configuration
- Initializes empty session and tools list

##### `async connect()`
```python
async def connect(self):
    # 1. Set up server parameters
    server_params = StdioServerParameters(
        command=self.server_python,  # .venv/bin/python
        args=["-m", "barry_server.server"],
        env={"PYTHONPATH": str(self.server_path / "src")}
    )
    
    # 2. Start server subprocess via stdio
    self.stdio_context = stdio_client(server_params)
    self.read_stream, self.write_stream = await self.stdio_context.__aenter__()
    
    # 3. Create MCP session
    self.session = ClientSession(self.read_stream, self.write_stream)
    
    # 4. Start session (background communication)
    await self.session.__aenter__()
    
    # 5. Initialize session (handshake)
    await asyncio.wait_for(self.session.initialize(), timeout=10.0)
    
    # 6. List available tools
    response = await self.session.list_tools()
    self.tools = response.tools
```

**Connection Flow:**
1. **Server Parameters** - Define how to start Barry server
2. **stdio_client** - Creates subprocess with stdin/stdout pipes
3. **ClientSession** - MCP session for communication
4. **Session Start** - Begins background message handling
5. **Initialize** - MCP handshake (protocol version, capabilities)
6. **List Tools** - Fetch available tools from server

**Critical Fix:** Using `await self.session.__aenter__()` to properly start the session before initializing.

##### `async call_tool(tool_name, arguments)`
```python
async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
    # Execute tool call via MCP
    result = await self.session.call_tool(tool_name, arguments)
    
    # Extract text content from result
    return "\n".join(
        item.text for item in result.content 
        if hasattr(item, 'text')
    )
```

**What it does:**
- Sends tool call request to Barry server
- Waits for response
- Extracts text content from MCP response format

##### `get_tools_schema()`
```python
def get_tools_schema(self) -> list[dict]:
    gemini_tools = []
    for tool in self.tools:
        gemini_tool = {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
        gemini_tools.append(gemini_tool)
    return gemini_tools
```

**Purpose:** Converts MCP tool schemas to format Gemini can understand

---

### 3. **gemini_agent.py** - Gemini Integration

#### **Class: GeminiAgent**

**Purpose:** Integrates Gemini API with MCP tools for natural language queries

##### `__init__(api_key, mcp_client)`
```python
def __init__(self, api_key: str, mcp_client: BarryMCPClient):
    # Create Gemini client
    self.client = genai.Client(api_key=api_key)
    
    # Convert MCP tools to Gemini format
    tools_schema = mcp_client.get_tools_schema()
    self.function_declarations = self._convert_tools_to_gemini(tools_schema)
```

**Initialization:**
1. Create Gemini API client
2. Get MCP tool schemas
3. Convert to Gemini function declarations

##### `_convert_tools_to_gemini(tools_schema)`
```python
def _convert_tools_to_gemini(self, tools_schema: list[dict]):
    function_declarations = []
    
    for tool in tools_schema:
        # Convert properties
        properties = {}
        for prop_name, prop_schema in tool["parameters"]["properties"].items():
            prop_type = prop_schema.get("type", "string").upper()
            properties[prop_name] = types.Schema(
                type=types.Type[prop_type],
                description=prop_schema.get("description", ""),
                enum=prop_schema.get("enum") if prop_schema.get("enum") else None
            )
        
        # Create function declaration
        func_decl = types.FunctionDeclaration(
            name=tool["name"],
            description=tool["description"],
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties=properties,
                required=tool["parameters"].get("required", [])
            )
        )
        function_declarations.append(func_decl)
    
    return function_declarations
```

**Schema Conversion:**
- **MCP format** → **Gemini FunctionDeclaration**
- Converts JSON schema types to Gemini types
- Preserves descriptions, enums, required fields

##### `async send_message(message)`
```python
async def send_message(self, message: str) -> str:
    # 1. Create chat with tools
    chat = self.client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=self.function_declarations)],
            temperature=0.7
        )
    )
    
    # 2. Send initial message
    response = chat.send_message(message)
    
    # 3. Handle function calls
    while response.candidates[0].content.parts:
        part = response.candidates[0].content.parts[0]
        
        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
            
            # Execute via MCP
            result = await self.mcp_client.call_tool(
                function_call.name,
                dict(function_call.args)
            )
            
            # Send result back to Gemini
            response = chat.send_message(
                f"Here is the data from the {function_call.name} function:\n\n{result}\n\nPlease format this nicely for the user."
            )
        else:
            break
    
    # 4. Get final text response
    return response.text
```

**Message Flow:**
1. **Create Chat** - Initialize Gemini chat with tools
2. **Send Message** - User query to Gemini
3. **Function Call Loop:**
   - Check if Gemini wants to call a function
   - Execute function via MCP client
   - Send result back to Gemini
   - Repeat until no more function calls
4. **Final Response** - Gemini's formatted answer

**Critical Fix:** Sending tool results as plain text with instructions to format, not as `Content` objects.

---

## 🔄 Data Flow

### Complete Query Execution

**User Query:** "Give me 5 dark chocolate callets"

```
1. User Input (gemini_agent.py:192)
   ↓
   user_input = "Give me 5 dark chocolate callets"

2. Send to Gemini (gemini_agent.py:94)
   ↓
   response = chat.send_message(message)
   
3. Gemini Analyzes Query
   ↓
   Decides to use: query_chocolate_products
   Arguments: {
     "chocolate_type": "Dark",
     "moulding_type": "callets",
     "n": 5
   }

4. Function Call Detected (gemini_agent.py:101)
   ↓
   if hasattr(part, 'function_call') and part.function_call:

5. Execute via MCP Client (gemini_agent.py:109)
   ↓
   result = await self.mcp_client.call_tool(
       "query_chocolate_products",
       {"chocolate_type": "Dark", "moulding_type": "callets", "n": 5}
   )

6. MCP Client Calls Server (client.py:95)
   ↓
   result = await self.session.call_tool(tool_name, arguments)

7. Barry Server Processes (server.py:260-339)
   ↓
   - Filter by Product_Type: "chocolate"
   - Filter by Base_Type: "Dark"
   - Filter by Moulding_Type: contains "callets"
   - Validate Material_Code: starts with "CHD-"
   - Return top 5 results with descriptions

8. Results Flow Back
   ↓
   Server → MCP Client → Gemini Agent
   (3162 chars of formatted chocolate data)

9. Send to Gemini (gemini_agent.py:117)
   ↓
   response = chat.send_message(
       f"Here is the data...\n\n{result}\n\nPlease format this nicely..."
   )

10. Gemini Formats Response
    ↓
    Gemini reads the data and creates a nice formatted response

11. Display to User (gemini_agent.py:131)
    ↓
    print(f"\n🤖 Gemini: {final_response}")
```

---

## 🚀 Setup & Usage

### Installation

```bash
# 1. Navigate to project
cd /Users/samyamoyrakshit/Documents/MCP\ Servers/barry-client

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e .
```

### Configuration

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your Gemini API key
GEMINI_API_KEY=your_actual_api_key_here
BARRY_SERVER_PATH=/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server
BARRY_SERVER_PYTHON=/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server/.venv/bin/python
```

### Running

```bash
# Start the client
PYTHONPATH=src python src/barry_client/gemini_agent.py
```

### Example Session

```
🚀 Starting Barry MCP Client...
  → Connecting to server...
  → Session initialized: barry-server
✓ Connected to Barry MCP Server
✓ Available tools: 2

🤖 Initializing Gemini Agent...
✓ Initialized Gemini with 2 tools

============================================================
Barry MCP Client with Gemini - Ready!
============================================================

You: Give me 5 dark chocolate callets

💬 You: Give me 5 dark chocolate callets

🔧 Gemini calling tool: query_chocolate_products
   Arguments: {'chocolate_type': 'Dark', 'moulding_type': 'callets', 'n': 5}
✓ Tool result received (3162 chars)

🤖 Gemini: Here are 5 dark chocolate callets:

1. **CHD-12345** - Dark Chocolate Callets 70%
   Fat: 35.2g
   Base: Dark | Moulding: Callets
   Description: Premium dark chocolate callets...

[... more results ...]
```

---

## 🎓 How Everything Works Together

### Startup Sequence

```
1. User runs: PYTHONPATH=src python src/barry_client/gemini_agent.py
   ↓
2. main() loads environment variables (.env)
   ↓
3. Creates BarryMCPClient instance
   ↓
4. Calls await mcp_client.connect()
   ├─ Starts Barry server subprocess
   ├─ Creates MCP session
   ├─ Initializes protocol handshake
   └─ Lists available tools
   ↓
5. Creates GeminiAgent instance
   ├─ Initializes Gemini API client
   ├─ Converts MCP tools to Gemini format
   └─ Ready to handle queries
   ↓
6. Enters conversation loop
   └─ Waits for user input
```

### Query Processing

```
User Query
    ↓
Gemini API
    ├─ Understands intent
    ├─ Decides which tool to use
    └─ Extracts parameters
    ↓
MCP Client
    ├─ Sends tool call to server
    └─ Receives results
    ↓
Barry Server
    ├─ Queries pandas DataFrame
    ├─ Filters data
    └─ Formats results
    ↓
Results flow back up
    ↓
Gemini formats final response
    ↓
User sees answer
```

### Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Protocol** | MCP (Model Context Protocol) | Client-server communication |
| **Transport** | stdio (stdin/stdout) | Subprocess communication |
| **AI Model** | Gemini 2.5 Flash | Natural language understanding |
| **Function Calling** | Gemini Function Declarations | Tool integration |
| **Data Processing** | Pandas (server-side) | Dataset queries |
| **Async Runtime** | asyncio | Concurrent operations |

---

## 🐛 Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not set"**
- Solution: Create `.env` file with your API key

**2. "Session initialization timeout"**
- Cause: Barry server not responding
- Solution: Check if server can start manually:
  ```bash
  cd ../barry-mcp-server
  PYTHONPATH=src .venv/bin/python -m barry_server.server
  ```

**3. "429 RESOURCE_EXHAUSTED"**
- Cause: Gemini API quota exceeded
- Solution: Wait for quota reset or use different model

**4. "models/gemini-X not found"**
- Cause: Model name not available in new SDK
- Solution: Use `gemini-2.5-flash` or `gemini-2.5-pro`

---

## 📊 Performance Characteristics

- **Startup Time:** ~3-5 seconds (server loading + MCP handshake)
- **Query Time:** ~1-2 seconds (MCP call + Gemini processing)
- **Memory Usage:** ~250MB (client + server + dataset)
- **Dataset Size:** 44,538 unique SKUs in memory

---

## 🎯 Key Achievements

1. ✅ Successfully integrated MCP with Gemini API
2. ✅ Implemented proper async/await patterns
3. ✅ Fixed stdio communication (stderr for logs, stdout for MCP)
4. ✅ Converted tool schemas between MCP and Gemini formats
5. ✅ Handled function calling loop correctly
6. ✅ Created working terminal chat interface

---

## 🔑 Critical Implementation Details

### Why stderr for Server Logs?

```python
# WRONG - interferes with MCP protocol
print("Server ready!")

# RIGHT - MCP uses stdout for protocol
print("Server ready!", file=sys.stderr)
```

**Reason:** MCP uses stdout for JSON-RPC messages. Any print to stdout corrupts the protocol.

### Why Plain Text Function Responses?

```python
# WRONG - Gemini SDK rejects Content objects
response = chat.send_message(
    types.Content(parts=[types.Part(function_response=...)])
)

# RIGHT - Send as plain text with instructions
response = chat.send_message(
    f"Here is the data...\n\n{result}\n\nPlease format this nicely..."
)
```

**Reason:** New `google-genai` SDK expects function responses as user messages, not Content objects.

### Why Session __aenter__?

```python
# WRONG - session not started
await self.session.initialize()

# RIGHT - start session first
await self.session.__aenter__()
await self.session.initialize()
```

**Reason:** MCP ClientSession needs to start background message handling before initialization.

---

## 📚 Learning Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Google GenAI Python](https://github.com/googleapis/python-genai)

---

## 🎉 Summary

The Barry MCP Client successfully demonstrates:
- **MCP Protocol** - Remote client connecting to MCP server
- **Gemini Integration** - Function calling with tool execution
- **Async Python** - Proper async/await patterns
- **stdio Communication** - Subprocess management
- **Schema Conversion** - MCP ↔ Gemini format translation

**Total Implementation:** ~345 lines of clean, well-documented Python code that bridges two powerful technologies (MCP and Gemini) to enable natural language queries over a local chocolate product dataset.

---

**Created:** 2026-01-22  
**Version:** 1.0.0  
**Status:** ✅ Fully Functional
