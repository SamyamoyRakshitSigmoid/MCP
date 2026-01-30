# Model Context Protocol (MCP) - Comprehensive Documentation

**Author:** Samyamoy Rakshit  
**Date:** January 30, 2026  
**Purpose:** Technical documentation for management review

---

## Table of Contents

1. [What is MCP?](#1-what-is-mcp)
2. [MCP vs Traditional Gen AI](#2-mcp-vs-traditional-gen-ai)
3. [MCP Architecture](#3-mcp-architecture)
4. [MCP Transport Layers](#4-mcp-transport-layers)
5. [FastMCP vs Traditional MCP](#5-fastmcp-vs-traditional-mcp)
6. [Implementation: Barry Server & Client](#6-implementation-barry-server--client)
7. [LLM Flexibility in MCP](#7-llm-flexibility-in-mcp)

---

## 1. What is MCP?

### Definition

**Model Context Protocol (MCP)** is an open protocol that standardizes how AI applications (like Claude, ChatGPT, or local LLMs) connect to external data sources and tools.

Think of MCP as **USB for AI** - just as USB provides a standard way for devices to connect to computers, MCP provides a standard way for AI models to connect to tools and data.

### Key Concepts for Beginners

**Analogy:** Imagine you're a chef (the AI model):
- **Traditional approach:** You need to learn how each kitchen appliance works differently
- **MCP approach:** All appliances have the same interface - you just need to learn MCP once

**In technical terms:**
- **MCP Server:** A program that exposes tools/data (like a chocolate product database)
- **MCP Client:** A program that connects to MCP servers and uses their tools
- **LLM/AI Model:** The intelligence that decides when and how to use the tools

### Real-World Example

```
User: "Show me 5 dark chocolate callets"
  ↓
AI Model (Claude/Gemini/Ollama): Understands the request
  ↓
MCP Client: Connects to Barry Server
  ↓
MCP Server: Queries chocolate database
  ↓
Returns: 5 dark chocolate products
  ↓
AI Model: Formats and presents results to user
```

---

## 2. MCP vs Traditional Gen AI

### Architectural Differences

#### Traditional Gen AI Architecture

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│                   Your Application                   │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Hardcoded Logic for Each LLM                  │ │
│  │                                                 │ │
│  │  if llm == "openai":                           │ │
│  │      use OpenAI API format                     │ │
│  │  elif llm == "anthropic":                      │ │
│  │      use Anthropic API format                  │ │
│  │  elif llm == "gemini":                         │ │
│  │      use Gemini API format                     │ │
│  │                                                 │ │
│  │  # Custom code for each tool                   │ │
│  │  # Custom code for each data source            │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    OpenAI API    Anthropic API   Gemini API
```

**Problems:**
- ❌ Tightly coupled to specific LLM APIs
- ❌ Need to rewrite code for each new LLM
- ❌ Tools and data sources are hardcoded
- ❌ Difficult to maintain and scale

#### MCP Architecture

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              Any LLM (Claude/Gemini/Ollama)         │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ MCP Protocol (Standardized)
                   │
         ┌─────────▼─────────┐
         │                   │
         │    MCP Client     │
         │                   │
         └─────────┬─────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Server │ │ Server │ │ Server │
   │   1    │ │   2    │ │   3    │
   └────────┘ └────────┘ └────────┘
   (Database) (API)     (Files)
```

**Advantages:**
- ✅ Decoupled from specific LLMs
- ✅ Switch LLMs by changing one configuration
- ✅ Reusable tools across different AI applications
- ✅ Easy to add new data sources

### Key Differences Table

| Aspect | Traditional Gen AI | MCP |
|--------|-------------------|-----|
| **LLM Integration** | Hardcoded for each LLM | Standardized protocol |
| **Tool Definition** | Custom code per LLM | Universal tool schema |
| **Switching LLMs** | Rewrite significant code | Change config file |
| **Data Sources** | Tightly coupled | Loosely coupled via servers |
| **Maintainability** | High complexity | Low complexity |
| **Reusability** | Limited | High |

---

## 3. MCP Architecture

### Core Components

#### 1. MCP Server

**Purpose:** Exposes tools and data to AI models

**Responsibilities:**
- Define available tools (functions the AI can call)
- Execute tool calls
- Return structured data
- Handle errors

**Example (Barry Server):**
```python
# Server exposes 2 tools:
1. query_skus_by_fat(fat_value, operator, n)
2. query_chocolate_products(chocolate_type, moulding_type, n)
```

#### 2. MCP Client

**Purpose:** Connects to MCP servers and facilitates communication

**Responsibilities:**
- Establish connection to servers
- List available tools
- Execute tool calls on behalf of AI
- Convert tool schemas for different LLMs

#### 3. LLM/AI Model

**Purpose:** Provides intelligence and natural language understanding

**Responsibilities:**
- Understand user requests
- Decide which tools to use
- Format responses for users
- Handle conversation flow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: User asks a question                                │
│ "Show me 5 dark chocolate callets"                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: LLM analyzes the request                            │
│ - Understands: User wants chocolate products                │
│ - Identifies: Need to query database                        │
│ - Decides: Use query_chocolate_products tool                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: LLM calls tool via MCP Client                       │
│ Tool: query_chocolate_products                              │
│ Args: {chocolate_type: "Dark", moulding_type: "callets",    │
│        n: 5}                                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: MCP Client forwards to MCP Server                   │
│ Protocol: JSON-RPC over stdio/HTTP/SSE                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: MCP Server executes tool                            │
│ - Filters pandas DataFrame                                  │
│ - Applies filters: Base_Type="Dark", Moulding="callets"    │
│ - Returns top 5 results                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Results flow back through MCP Client                │
│ Data: [Product1, Product2, Product3, Product4, Product5]    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 7: LLM formats and presents results                    │
│ "Here are 5 dark chocolate callets:                         │
│  1. CHD-12345 - Dark Chocolate Callets 70%                  │
│  2. CHD-67890 - Organic Dark Callets..."                    │
└─────────────────────────────────────────────────────────────┘
```

### Beginner Example: Calculator Analogy

**Imagine MCP as a calculator system:**

```
You (User): "What's 25 + 37?"
  ↓
Brain (LLM): "I need to add numbers, I'll use the calculator"
  ↓
Hands (MCP Client): Picks up calculator and presses buttons
  ↓
Calculator (MCP Server): Performs calculation
  ↓
Display (Result): Shows "62"
  ↓
Brain (LLM): "The answer is 62"
  ↓
You hear: "The answer is 62"
```

**Key insight:** The brain (LLM) doesn't do the math - it just knows WHEN to use the calculator and HOW to interpret results.

---

## 4. MCP Transport Layers

### What are Transport Layers?

**Definition:** Transport layers are the communication methods used to send messages between MCP clients and servers.

**Analogy:** Think of different ways to send a letter:
- **stdio:** Hand-delivering a letter directly
- **HTTP:** Sending via postal service
- **SSE:** Subscribing to a newsletter that sends updates

### Types of Transport Layers

#### 1. stdio (Standard Input/Output)

**How it works:**
- Server runs as a subprocess
- Communication via stdin (input) and stdout (output)
- Like two programs talking through pipes

**Diagram:**
```
┌──────────────┐         stdin/stdout         ┌──────────────┐
│              │ ◄─────────────────────────► │              │
│  MCP Client  │                              │  MCP Server  │
│              │         (pipes)              │  (subprocess)│
└──────────────┘                              └──────────────┘
```

**Use Case:** Local development, Claude Desktop integration

**Example (Barry Server with Claude Desktop):**
```json
{
  "mcpServers": {
    "barry-server": {
      "command": "/path/to/python",
      "args": ["-m", "barry_server.server"]
    }
  }
}
```

**Pros:**
- ✅ Simple and fast
- ✅ No network overhead
- ✅ Secure (local only)
- ✅ Easy to debug

**Cons:**
- ❌ Only works locally
- ❌ Server must be on same machine

#### 2. HTTP (HyperText Transfer Protocol)

**How it works:**
- Server runs as a web service
- Client makes HTTP requests
- Like accessing a website

**Diagram:**
```
┌──────────────┐      HTTP Requests       ┌──────────────┐
│              │ ────────────────────────► │              │
│  MCP Client  │                           │  MCP Server  │
│              │ ◄──────────────────────── │  (Web API)   │
└──────────────┘      HTTP Responses      └──────────────┘
```

**Use Case:** Remote servers, cloud deployments, multiple clients

**Example:**
```python
# Server runs at: http://api.example.com:8000
# Client connects via HTTP
client = MCPClient("http://api.example.com:8000")
```

**Pros:**
- ✅ Works over network
- ✅ Multiple clients can connect
- ✅ Scalable
- ✅ Standard protocol

**Cons:**
- ❌ Network latency
- ❌ Requires server setup
- ❌ Need to handle authentication

#### 3. SSE (Server-Sent Events)

**How it works:**
- Server pushes updates to client
- Client maintains open connection
- Like a live news feed

**Diagram:**
```
┌──────────────┐    Initial Connection    ┌──────────────┐
│              │ ────────────────────────► │              │
│  MCP Client  │                           │  MCP Server  │
│              │ ◄──────────────────────── │  (SSE)       │
└──────────────┘    Continuous Stream     └──────────────┘
```

**Use Case:** Real-time updates, streaming responses, live data

**Example:**
```python
# Server sends updates as they happen
# Client receives them in real-time
# Useful for: live cricket scores, stock prices, etc.
```

**Pros:**
- ✅ Real-time updates
- ✅ Server can push data
- ✅ Efficient for streaming
- ✅ Built on HTTP

**Cons:**
- ❌ More complex
- ❌ One-way communication (server → client)
- ❌ Requires persistent connection

### Comparison Table

| Feature | stdio | HTTP | SSE |
|---------|-------|------|-----|
| **Location** | Local only | Remote | Remote |
| **Speed** | Fastest | Medium | Medium |
| **Complexity** | Simplest | Medium | Complex |
| **Real-time** | No | No | Yes |
| **Multiple Clients** | No | Yes | Yes |
| **Best For** | Development | Production | Streaming |

### When to Use Each

#### Use stdio when:
- ✅ Developing locally
- ✅ Integrating with Claude Desktop
- ✅ Server and client on same machine
- ✅ You want simplest setup

**Example:** Barry Server with Claude Desktop (our implementation)

#### Use HTTP when:
- ✅ Server is remote
- ✅ Multiple clients need access
- ✅ You need standard web protocols
- ✅ Deploying to cloud

**Example:** Company-wide MCP server for product database

#### Use SSE when:
- ✅ You need real-time updates
- ✅ Server pushes data to clients
- ✅ Streaming responses
- ✅ Live data feeds

**Example:** Live cricket scores, stock market data

### Beginner Example: Pizza Delivery

**stdio (Hand Delivery):**
- You make pizza at home
- Walk it to your neighbor
- Fastest, but only works nearby

**HTTP (Delivery Service):**
- Order pizza from restaurant
- They deliver to your address
- Works anywhere, takes longer

**SSE (Pizza Subscription):**
- Subscribe to daily pizza delivery
- They send you pizza every day
- Continuous service, real-time

---

## 5. FastMCP vs Traditional MCP

### What is Traditional MCP?

**Traditional MCP** uses the official MCP Python SDK with full protocol implementation.

**Characteristics:**
- Uses `mcp` package
- Full protocol compliance
- More boilerplate code
- Maximum flexibility

**Example (Traditional MCP Server):**
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("my-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_data",
            description="Get some data",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "get_data":
        result = fetch_data(arguments["query"])
        return [TextContent(type="text", text=result)]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, 
                     app.create_initialization_options())
```

### What is FastMCP?

**FastMCP** is a lightweight wrapper around MCP that reduces boilerplate code.

**Characteristics:**
- Uses `fastmcp` package
- Decorator-based syntax
- Less code
- Easier for beginners

**Example (FastMCP Server):**
```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def get_data(query: str) -> str:
    """Get some data"""
    return fetch_data(query)

if __name__ == "__main__":
    mcp.run()
```

### Code Comparison

#### Traditional MCP (Barry Server - Actual Implementation)

**Lines of Code:** ~367 lines

```python
# Imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create server
app = Server("barry-server")

# Define tools manually
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_skus_by_fat",
            description="Query Material_Code (SKUs)...",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of results",
                        "minimum": 1,
                        "default": 10
                    },
                    "fat_value": {
                        "type": "number",
                        "description": "Fat content threshold"
                    },
                    "operator": {
                        "type": "string",
                        "enum": ["==", "<", "<=", ">", ">="],
                        "default": ">"
                    }
                },
                "required": ["fat_value"]
            }
        )
    ]

# Handle tool calls
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "query_skus_by_fat":
        return await query_skus_by_fat(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# Implement tool logic
async def query_skus_by_fat(arguments: dict) -> list[TextContent]:
    n = arguments.get("n", 10)
    fat_value = arguments["fat_value"]
    operator = arguments.get("operator", ">")
    
    # ... filtering logic ...
    
    return [TextContent(type="text", text=result)]

# Main entry point
async def main():
    load_data()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream,
                     app.create_initialization_options())
```

#### FastMCP (Equivalent Implementation)

**Lines of Code:** ~150 lines (60% reduction)

```python
# Imports
from fastmcp import FastMCP

# Create server
mcp = FastMCP("barry-server")

# Define tool with decorator
@mcp.tool()
def query_skus_by_fat(
    fat_value: float,
    operator: str = ">",
    n: int = 10
) -> str:
    """
    Query Material_Code (SKUs) based on fat content.
    
    Args:
        fat_value: Fat content threshold (in grams)
        operator: Comparison operator (==, <, <=, >, >=)
        n: Number of results to return
    """
    # ... filtering logic ...
    return result

# Main entry point
if __name__ == "__main__":
    load_data()
    mcp.run()
```

### Key Differences

| Aspect | Traditional MCP | FastMCP |
|--------|----------------|---------|
| **Code Length** | More verbose | Concise |
| **Tool Definition** | Manual schema | Auto-generated from type hints |
| **Decorators** | `@app.list_tools()`, `@app.call_tool()` | `@mcp.tool()` |
| **Type Handling** | Manual `TextContent` wrapping | Automatic |
| **Learning Curve** | Steeper | Gentler |
| **Flexibility** | Maximum control | Simplified |
| **Best For** | Complex servers, full control | Quick prototypes, beginners |

### Which is Better?

**There's no absolute "better" - it depends on your use case:**

#### Use Traditional MCP when:

✅ **You need full protocol control**
- Custom initialization options
- Advanced error handling
- Complex tool schemas

✅ **You're building production systems**
- Need maximum flexibility
- Want explicit control over everything
- Building complex integrations

✅ **You want to learn MCP deeply**
- Understand the protocol
- See how everything works
- Build foundation knowledge

**Example use cases:**
- Enterprise-grade MCP servers
- Complex multi-tool systems
- Custom transport layers
- Advanced error handling requirements

#### Use FastMCP when:

✅ **You want rapid development**
- Quick prototypes
- Simple tools
- Minimal boilerplate

✅ **You're a beginner**
- Learning MCP concepts
- Building first server
- Want to focus on logic, not protocol

✅ **You have simple requirements**
- Few tools
- Standard use cases
- Don't need advanced features

**Example use cases:**
- Personal projects
- Internal tools
- Proof of concepts
- Learning exercises

### Migration Path

**Good news:** You can start with FastMCP and migrate to Traditional MCP later if needed!

```python
# Start with FastMCP for rapid development
from fastmcp import FastMCP
mcp = FastMCP("my-server")

@mcp.tool()
def simple_tool(query: str) -> str:
    return process(query)

# Later, migrate to Traditional MCP for more control
from mcp.server import Server
app = Server("my-server")

@app.list_tools()
async def list_tools():
    # Now you have full control
    pass
```

### Our Implementation Choice

**We used Traditional MCP for Barry Server because:**

1. **Learning opportunity:** Understand MCP protocol deeply
2. **Full control:** Custom error handling and data formatting
3. **Production-ready:** Built for real-world use
4. **Flexibility:** Easy to extend with new features

**Result:** 367 lines of well-structured, production-ready code

---

## 6. Implementation: Barry Server & Client

### Project Overview

**Goal:** Enable AI models (Claude, Gemini, Ollama) to query a chocolate product dataset containing 44,538 unique SKUs.

**Components:**
1. **Barry MCP Server:** Exposes chocolate dataset via MCP tools
2. **Barry MCP Client:** Connects to server and integrates with different LLMs
3. **Three Integration Methods:** Claude Desktop (local), Gemini (cloud), Ollama (local)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│  "Show me 5 dark chocolate callets"                         │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐
│Claude  │ │Gemini  │ │Ollama  │
│Desktop │ │API     │ │Local   │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    │          ▼          │
    │    ┌──────────┐    │
    │    │  Barry   │    │
    │    │  Client  │    │
    │    └─────┬────┘    │
    │          │         │
    └──────────┼─────────┘
               │
               ▼
        ┌─────────────┐
        │   Barry     │
        │   Server    │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  Chocolate  │
        │  Dataset    │
        │  (44,538    │
        │   SKUs)     │
        └─────────────┘
```

---

### Barry MCP Server

#### What It Does

The server provides **2 tools** to query chocolate products:

1. **`query_skus_by_fat`** - Filter products by fat content
2. **`query_chocolate_products`** - Search by chocolate type and moulding

#### Technical Details

**Technology Stack:**
- Python 3.10+
- MCP SDK (`mcp` package)
- Pandas (data manipulation)
- stdio transport layer

**Data:**
- CSV file: 195MB
- Raw rows: 81,716
- Unique SKUs: 44,538 (after deduplication)
- Columns: 288

#### Server Code Structure

```python
# 1. Initialize server
app = Server("barry-server")
df: pd.DataFrame | None = None  # Global dataset

# 2. Load data
def load_data():
    # Multi-strategy path resolution
    # Load CSV with pandas
    # Deduplicate by Material_Code
    # Prefer EU legislation

# 3. Register tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    # Define 2 tools with schemas

# 4. Handle tool calls
@app.call_tool()
async def call_tool(name: str, arguments: Any):
    # Route to appropriate handler

# 5. Implement tools
async def query_skus_by_fat(arguments):
    # Filter by fat content
    # Return formatted results

async def query_chocolate_products(arguments):
    # Filter by type and moulding
    # Validate Material_Code prefix
    # Return formatted results

# 6. Main entry point
async def main():
    load_data()
    async with stdio_server() as (read, write):
        await app.run(read, write, options)
```

#### Tool 1: query_skus_by_fat

**Purpose:** Find products based on fat content

**Parameters:**
- `fat_value` (required): Fat threshold in grams
- `operator` (optional): Comparison operator (==, <, <=, >, >=), default: ">"
- `n` (optional): Number of results, default: 10

**Example:**
```
Input: fat_value=30, operator=">", n=5
Output: 5 products where Fat > 30g
```

**Implementation Logic:**
```python
# 1. Parse parameters
n = arguments.get("n", 10)
fat_value = arguments["fat_value"]
operator = arguments.get("operator", ">")

# 2. Use operator mapping (cleaner than if-elif)
operator_map = {
    "==": lambda x: x == fat_value,
    "<": lambda x: x < fat_value,
    "<=": lambda x: x <= fat_value,
    ">": lambda x: x > fat_value,
    ">=": lambda x: x >= fat_value,
}

# 3. Filter DataFrame
filtered = df[df["Fat"].apply(operator_map[operator])]

# 4. Format output with emoji indicators
📊 Found 5 SKU(s) where Fat > 30g:
  • CHD-12345 (Fat: 35.2g)
    📝 Dark Chocolate Callets 70%
    ℹ️  Material: Alcalised Powder cocoa...
```

#### Tool 2: query_chocolate_products

**Purpose:** Search for chocolate products by type and moulding

**Parameters:**
- `chocolate_type` (required): Dark, Milk, or White
- `moulding_type` (required): e.g., "callets", "chips", "blocks"
- `n` (optional): Number of results, default: 5

**Example:**
```
Input: chocolate_type="Dark", moulding_type="callets", n=5
Output: 5 dark chocolate callets
```

**Implementation Logic:**
```python
# 1. Material_Code prefix mapping
prefix_map = {
    "Dark": "CHD-",
    "Milk": "CHM-",
    "White": "CHW-"
}

# 2. Multi-stage filtering pipeline
filtered = df.copy()

# Step 1: Product_Type must be chocolate
filtered = filtered[
    filtered["Product_Type"].str.contains("chocolate", case=False)
]

# Step 2: Base_Type must match (Dark/Milk/White)
filtered = filtered[
    filtered["Base_Type"].str.lower() == chocolate_type.lower()
]

# Step 3: Moulding_Type flexible matching
filtered = filtered[
    filtered["Moulding_Type"].str.contains(moulding_type, case=False)
]

# Step 4: Validate Material_Code prefix
filtered = filtered[
    filtered["Material_Code"].str.startswith(expected_prefix)
]

# 5. Format output with validation checkmarks
🍫 Found 3 Dark chocolate product(s) with moulding type 'callets':
  ✓ CHD-12345
    📝 Dark Chocolate Callets 70%
    Base: Dark | Moulding: Callets
```

#### Key Design Decisions

**1. In-Memory Dataset**
- **Why:** Fast queries (no disk I/O)
- **Trade-off:** Uses ~200MB RAM
- **Benefit:** Instant responses (<100ms)

**2. Deduplication Strategy**
- **Why:** Same SKU appears for different regions (EU, US, RU)
- **Approach:** Keep one per Material_Code, prefer EU
- **Result:** 81,716 → 44,538 rows (45% reduction)

**3. Flexible String Matching**
- **Why:** User-friendly queries
- **Implementation:** `.str.contains()` for moulding types
- **Benefit:** "callets" matches "Callets", "Mini Callets", etc.

**4. Emoji Indicators**
- **Why:** Better visual feedback
- **Usage:** 📊 (stats), 📝 (description), ℹ️ (details), ✓/✗ (validation)
- **Benefit:** Easier to scan results

---

### Barry MCP Client

#### What It Does

The client connects to Barry Server and integrates with different LLMs (Gemini, Ollama).

**Note:** Claude Desktop doesn't need a separate client - it has built-in MCP support!

#### Client Code Structure

```python
class BarryMCPClient:
    def __init__(self, server_path: str, server_python: str):
        # Store server configuration
        
    async def connect(self):
        # 1. Set up server parameters
        # 2. Start server process via stdio
        # 3. Create MCP session
        # 4. Initialize session
        # 5. List available tools
        
    async def call_tool(self, tool_name: str, arguments: dict):
        # Execute tool call
        # Return formatted result
        
    def get_tools_schema(self):
        # Convert MCP tools to LLM format
        # Return tool schemas
```

#### How Client Works

**Connection Flow:**
```
1. Client creates stdio connection
   ↓
2. Spawns server as subprocess
   ↓
3. Establishes MCP session
   ↓
4. Lists available tools
   ↓
5. Ready to execute tool calls
```

**Tool Call Flow:**
```
1. LLM decides to use a tool
   ↓
2. Client receives tool call request
   ↓
3. Client forwards to server via stdio
   ↓
4. Server executes and returns result
   ↓
5. Client formats and returns to LLM
```

---

### Method 1: Claude Desktop (Local)

#### Overview

**Simplest method:** Claude Desktop has built-in MCP support - no client code needed!

#### How It Works

```
┌──────────────┐
│   You        │
│   ↓          │
│ Claude       │  Built-in MCP Client
│ Desktop      │  ↓
│              │  Spawns Barry Server
│              │  ↓
│              │  Queries chocolate data
└──────────────┘
```

#### Setup Process

**Step 1: Install Barry Server**
```bash
cd barry-mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Step 2: Configure Claude Desktop**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "barry-server": {
      "command": "/path/to/barry-mcp-server/.venv/bin/python",
      "args": ["-m", "barry_server.server"],
      "env": {
        "PYTHONPATH": "/path/to/barry-mcp-server/src"
      }
    }
  }
}
```

**Step 3: Restart Claude Desktop**

**Step 4: Verify Connection**

Look for 🔌 icon in Claude Desktop indicating server is connected.

#### Usage Example

```
You: Show me 5 dark chocolate callets

Claude: [Calls query_chocolate_products tool]
        [Receives results from Barry Server]
        [Formats and presents]

Here are 5 dark chocolate callets from the Barry dataset:

1. CHD-12345 - Dark Chocolate Callets 70%
   Fat: 35.2g
   Description: Premium dark chocolate callets...

2. CHD-67890 - Organic Dark Callets
   Fat: 33.1g
   Description: Certified organic dark chocolate...

[... more results ...]
```

#### Advantages

✅ **No client code needed** - Claude has built-in MCP support  
✅ **Simplest setup** - Just configure and run  
✅ **Local and private** - Data never leaves your machine  
✅ **Fast** - No network latency  

#### Disadvantages

❌ **Requires Claude Desktop** - Can't use other LLMs  
❌ **Local only** - Can't access remotely  

---

### Method 2: Gemini Integration (Cloud)

#### Overview

**Cloud-based approach:** Use Google's Gemini API with custom client.

#### Architecture

```
┌──────────────┐
│   You        │
│   ↓          │
│ Gemini       │  Custom Client
│ Agent        │  ↓
│ (Cloud API)  │  Connects to Barry Server
│              │  ↓
│              │  Queries chocolate data
└──────────────┘
```

#### Setup Process

**Step 1: Install Dependencies**
```bash
cd barry-client
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Step 2: Get Gemini API Key**

Visit: https://aistudio.google.com/app/apikey

**Step 3: Configure Environment**

Create `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
BARRY_SERVER_PATH=/path/to/barry-mcp-server
BARRY_SERVER_PYTHON=/path/to/barry-mcp-server/.venv/bin/python
```

**Step 4: Run Gemini Agent**
```bash
python -m barry_client.gemini_agent
```

#### Gemini Agent Code

```python
class GeminiAgent:
    def __init__(self, api_key: str, mcp_client: BarryMCPClient):
        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)
        
        # Convert MCP tools to Gemini format
        tools_schema = mcp_client.get_tools_schema()
        self.function_declarations = self._convert_tools_to_gemini(tools_schema)
    
    def _convert_tools_to_gemini(self, tools_schema):
        # Convert MCP schema to Gemini FunctionDeclaration
        # Gemini requires specific type format:
        # types.Schema(type=types.Type.STRING, ...)
        
    async def send_message(self, message: str):
        # Create chat with tools
        chat = self.client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=self.function_declarations)]
            )
        )
        
        # Send message
        response = chat.send_message(message)
        
        # Handle function calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            if hasattr(part, 'function_call'):
                # Execute tool via MCP client
                result = await self.mcp_client.call_tool(
                    part.function_call.name,
                    dict(part.function_call.args)
                )
                
                # Send result back to Gemini
                response = chat.send_message(
                    f"Here is the data: {result}"
                )
            else:
                break
        
        return response.text
```

#### Tool Schema Conversion

**MCP Schema:**
```python
{
    "name": "query_skus_by_fat",
    "description": "Query SKUs by fat content",
    "parameters": {
        "type": "object",
        "properties": {
            "fat_value": {"type": "number"},
            "operator": {"type": "string", "enum": ["==", "<", ">"]},
            "n": {"type": "integer", "default": 10}
        },
        "required": ["fat_value"]
    }
}
```

**Gemini Format:**
```python
types.FunctionDeclaration(
    name="query_skus_by_fat",
    description="Query SKUs by fat content",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "fat_value": types.Schema(type=types.Type.NUMBER),
            "operator": types.Schema(
                type=types.Type.STRING,
                enum=["==", "<", ">"]
            ),
            "n": types.Schema(type=types.Type.INTEGER)
        },
        required=["fat_value"]
    )
)
```

#### Advantages

✅ **Cloud-based** - No local LLM needed  
✅ **Latest Gemini models** - Access to Google's newest AI  
✅ **Scalable** - No hardware limitations  

#### Disadvantages

❌ **Requires API key** - Need Google account  
❌ **Network latency** - Cloud communication overhead  
❌ **Cost** - Pay per API call  
❌ **Complex code** - Type conversion required (~204 lines)  

---

### Method 3: Ollama Integration (Local)

#### Overview

**Open-source approach:** Use local LLMs via Ollama with custom client.

#### Architecture

```
┌──────────────┐
│   You        │
│   ↓          │
│ Ollama       │  Custom Client
│ Agent        │  ↓
│ (Local LLM)  │  Connects to Barry Server
│              │  ↓
│              │  Queries chocolate data
└──────────────┘
```

#### Setup Process

**Step 1: Install Ollama**
```bash
brew install ollama
```

**Step 2: Start Ollama Server**
```bash
ollama serve
```

**Step 3: Pull a Model**
```bash
ollama pull qwen2.5-coder:7b
# or
ollama pull llama3.1:latest
```

**Step 4: Configure Environment**

Create `.env` file:
```bash
OLLAMA_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434
BARRY_SERVER_PATH=/path/to/barry-mcp-server
BARRY_SERVER_PYTHON=/path/to/barry-mcp-server/.venv/bin/python
```

**Step 5: Run Ollama Agent**
```bash
python -m barry_client.ollama_agent
```

#### Ollama Agent Code

```python
class OllamaAgent:
    def __init__(self, model: str, mcp_client: BarryMCPClient, base_url: str):
        # Initialize Ollama client
        self.client = ollama.Client(host=base_url)
        
        # Convert MCP tools to Ollama format (simpler!)
        tools_schema = mcp_client.get_tools_schema()
        self.tools = self._convert_tools_to_ollama(tools_schema)
        
        # Conversation history
        self.messages = []
    
    def _convert_tools_to_ollama(self, tools_schema):
        # Ollama accepts standard JSON schema - just wrap it!
        ollama_tools = []
        for tool in tools_schema:
            ollama_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]  # Pass through!
                }
            }
            ollama_tools.append(ollama_tool)
        return ollama_tools
    
    async def send_message(self, message: str):
        # Add to conversation history
        self.messages.append({
            "role": "user",
            "content": message
        })
        
        # Chat with Ollama
        response = self.client.chat(
            model=self.model,
            messages=self.messages,
            tools=self.tools
        )
        
        # Handle tool calls
        while response.get('message', {}).get('tool_calls'):
            # Add assistant's response to history
            self.messages.append(response['message'])
            
            # Execute each tool call
            for tool_call in response['message']['tool_calls']:
                function_name = tool_call['function']['name']
                function_args = tool_call['function']['arguments']
                
                # Execute via MCP client
                result = await self.mcp_client.call_tool(
                    function_name,
                    function_args
                )
                
                # Add tool result to history
                self.messages.append({
                    "role": "tool",
                    "content": result
                })
            
            # Continue conversation
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self.tools
            )
        
        # Add final response to history
        self.messages.append(response['message'])
        
        return response['message']['content']
```

#### Tool Schema Conversion

**MCP Schema:**
```python
{
    "name": "query_skus_by_fat",
    "description": "Query SKUs by fat content",
    "parameters": {
        "type": "object",
        "properties": {
            "fat_value": {"type": "number"},
            "operator": {"type": "string"},
            "n": {"type": "integer"}
        }
    }
}
```

**Ollama Format:**
```python
{
    "type": "function",
    "function": {
        "name": "query_skus_by_fat",
        "description": "Query SKUs by fat content",
        "parameters": {
            "type": "object",
            "properties": {
                "fat_value": {"type": "number"},
                "operator": {"type": "string"},
                "n": {"type": "integer"}
            }
        }
    }
}
```

**Key difference:** Ollama accepts standard JSON schema - no complex type conversion!

#### Advantages

✅ **No API key needed** - Completely free  
✅ **Privacy** - Data never leaves your machine  
✅ **Simple code** - ~180 lines (12% less than Gemini)  
✅ **Flexible** - Easy to switch models  
✅ **Fast** - Local inference, no network latency  

#### Disadvantages

❌ **Requires local resources** - Need GPU/CPU for inference  
❌ **Model quality** - May not match cloud models  
❌ **Setup complexity** - Need to install Ollama  

---

### Comparison of Three Methods

| Aspect | Claude Desktop | Gemini | Ollama |
|--------|---------------|--------|--------|
| **Setup Complexity** | Simplest | Medium | Medium |
| **Code Required** | None | ~204 lines | ~180 lines |
| **API Key** | No | Yes | No |
| **Cost** | Free/Pro | Pay per call | Free |
| **Privacy** | Local | Cloud | Local |
| **Speed** | Fast | Medium | Fast |
| **Model Quality** | Excellent | Excellent | Good |
| **Flexibility** | Low | High | High |
| **Best For** | Quick setup | Cloud deployment | Open-source fans |

---

## 7. LLM Flexibility in MCP

### The Key Advantage

**With MCP, switching LLMs requires minimal code changes!**

### What Changes When Switching LLMs

#### In MCP Architecture

**Files that change:**
- ✅ **One agent file** (gemini_agent.py OR ollama_agent.py)
- ✅ **One config file** (.env)

**Files that stay the same:**
- ✅ **server.py** - No changes needed!
- ✅ **client.py** - No changes needed!
- ✅ **Data files** - No changes needed!

#### Example: Switching from Gemini to Ollama

**Step 1: Create new agent file**

Only need to change ~30 lines for tool conversion:

```python
# gemini_agent.py (Complex conversion)
def _convert_tools_to_gemini(self, tools_schema):
    # 30+ lines of type conversion
    properties = {}
    for prop_name, prop_schema in tool["parameters"]["properties"].items():
        prop_type = prop_schema.get("type", "string").upper()
        properties[prop_name] = types.Schema(
            type=types.Type[prop_type],
            description=prop_schema.get("description", "")
        )
    # ... more conversion logic ...

# ollama_agent.py (Simple pass-through)
def _convert_tools_to_ollama(self, tools_schema):
    # 10 lines - just wrap it!
    return [{
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]  # Pass through!
        }
    } for tool in tools_schema]
```

**Step 2: Update config**

```bash
# .env for Gemini
GEMINI_API_KEY=your_key

# .env for Ollama
OLLAMA_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434
```

**Step 3: Run different agent**

```bash
# Gemini
python -m barry_client.gemini_agent

# Ollama
python -m barry_client.ollama_agent
```

**That's it!** Server and client code remain unchanged.

---

### Comparison with Traditional Gen AI

#### Traditional Gen AI Approach

**If we built this WITHOUT MCP:**

```python
# chocolate_query_app.py

def query_with_openai(query: str):
    # Custom code for OpenAI
    prompt = f"Query chocolate database: {query}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    # Parse response
    # Manually extract parameters
    # Query database
    # Format results
    # Return to OpenAI for formatting
    
def query_with_anthropic(query: str):
    # COMPLETELY DIFFERENT code for Anthropic
    prompt = f"Query chocolate database: {query}"
    response = anthropic.Completions.create(
        model="claude-3",
        prompt=prompt
    )
    # Different parsing logic
    # Different parameter extraction
    # Same database query
    # Different formatting
    # Return to Anthropic
    
def query_with_gemini(query: str):
    # ANOTHER DIFFERENT implementation for Gemini
    # ... completely rewritten logic ...
    
# Main app
if llm_choice == "openai":
    result = query_with_openai(user_query)
elif llm_choice == "anthropic":
    result = query_with_anthropic(user_query)
elif llm_choice == "gemini":
    result = query_with_gemini(user_query)
```

**Problems:**
- ❌ Need to rewrite logic for each LLM
- ❌ Tightly coupled to LLM APIs
- ❌ Hard to maintain
- ❌ Can't reuse tools across projects

#### MCP Approach

**With MCP:**

```python
# server.py - NEVER CHANGES
@app.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "query_chocolate_products":
        return await query_chocolate_products(arguments)

# client.py - NEVER CHANGES
async def call_tool(self, tool_name: str, arguments: dict):
    result = await self.session.call_tool(tool_name, arguments)
    return result

# gemini_agent.py - ONLY THIS CHANGES
class GeminiAgent:
    def __init__(self, api_key, mcp_client):
        self.client = genai.Client(api_key=api_key)
        # Tool conversion specific to Gemini
        
# ollama_agent.py - OR THIS CHANGES
class OllamaAgent:
    def __init__(self, model, mcp_client):
        self.client = ollama.Client()
        # Tool conversion specific to Ollama
```

**Advantages:**
- ✅ Server code is reusable
- ✅ Client code is reusable
- ✅ Only agent layer changes
- ✅ Easy to add new LLMs
- ✅ Tools work across all LLMs

---

### Visual Comparison

#### Traditional Gen AI: Tightly Coupled

```
┌─────────────────────────────────────────┐
│         Your Application                │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  if llm == "openai":              │ │
│  │      # Custom OpenAI logic        │ │
│  │      # Custom database query      │ │
│  │      # Custom formatting          │ │
│  │                                   │ │
│  │  elif llm == "anthropic":         │ │
│  │      # REWRITE EVERYTHING         │ │
│  │                                   │ │
│  │  elif llm == "gemini":            │ │
│  │      # REWRITE AGAIN              │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**To switch LLMs:** Rewrite significant portions of code

#### MCP: Loosely Coupled

```
┌─────────────────────────────────────────┐
│         LLM Layer (Swappable)           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Gemini   │  │ Ollama   │  │ Claude ││
│  │ Agent    │  │ Agent    │  │ Desktop││
│  └────┬─────┘  └────┬─────┘  └───┬────┘│
└───────┼─────────────┼────────────┼──────┘
        │             │            │
        └─────────────┼────────────┘
                      │
┌─────────────────────▼─────────────────────┐
│         MCP Client (Reusable)             │
└─────────────────────┬─────────────────────┘
                      │
┌─────────────────────▼─────────────────────┐
│         MCP Server (Reusable)             │
│         - query_skus_by_fat               │
│         - query_chocolate_products        │
└───────────────────────────────────────────┘
```

**To switch LLMs:** Change agent file and config

---

### Code Reusability Statistics

#### Traditional Gen AI

**Lines of code per LLM:**
- OpenAI implementation: ~500 lines
- Anthropic implementation: ~500 lines
- Gemini implementation: ~500 lines

**Total:** ~1,500 lines (mostly duplicated logic)

**Reusable:** ~0% (each LLM needs custom code)

#### MCP Approach

**Lines of code:**
- Server (shared): ~367 lines
- Client (shared): ~139 lines
- Gemini agent: ~204 lines
- Ollama agent: ~180 lines

**Total:** ~890 lines

**Reusable:** ~57% (server + client work with all LLMs)

**Savings:** ~40% less code, ~100% more maintainable

---

### Real-World Impact

#### Scenario: Adding a New LLM

**Traditional Gen AI:**
1. Study new LLM's API
2. Rewrite database query logic
3. Rewrite parameter extraction
4. Rewrite result formatting
5. Test everything again
6. Maintain separate codebase

**Time:** 2-3 days

**MCP Approach:**
1. Create new agent file (~200 lines)
2. Implement tool conversion
3. Update config
4. Test (server/client already tested!)

**Time:** 2-3 hours

**Result:** 10x faster development!

---

### Summary: Why MCP Wins

#### For Developers

✅ **Write once, use everywhere** - Server code works with all LLMs  
✅ **Faster development** - Only agent layer changes  
✅ **Easier maintenance** - Less code to maintain  
✅ **Better testing** - Test server once, works for all LLMs  

#### For Organizations

✅ **Vendor independence** - Not locked into one LLM provider  
✅ **Cost optimization** - Easy to switch to cheaper LLMs  
✅ **Future-proof** - New LLMs work with existing tools  
✅ **Reusable infrastructure** - Tools work across projects  

#### For End Users

✅ **Consistent experience** - Same tools, different LLMs  
✅ **Better performance** - Choose best LLM for each task  
✅ **More options** - Use local or cloud LLMs  

---

## Conclusion

### What We Built

**Barry MCP Server & Client System:**
- ✅ MCP server exposing chocolate product database
- ✅ 2 powerful query tools
- ✅ 3 integration methods (Claude, Gemini, Ollama)
- ✅ Flexible, maintainable, production-ready code

### Key Learnings

**MCP Concepts:**
- MCP standardizes AI-tool communication
- Decouples LLMs from data sources
- Enables reusable, maintainable code

**Transport Layers:**
- stdio for local development
- HTTP for remote servers
- SSE for real-time updates

**FastMCP vs Traditional:**
- FastMCP: Simpler, faster development
- Traditional: More control, production-ready

**LLM Flexibility:**
- Switch LLMs with minimal code changes
- Server and client code is reusable
- 10x faster than traditional approach

### Future Possibilities

**Potential Enhancements:**
1. Add more tools (price queries, inventory checks)
2. Implement HTTP transport for remote access
3. Add authentication and security
4. Build web UI for non-technical users
5. Integrate with more LLMs (GPT-4, Claude 3, etc.)

---

**End of Documentation**

*For questions or clarifications, please contact: Samyamoy Rakshit*
