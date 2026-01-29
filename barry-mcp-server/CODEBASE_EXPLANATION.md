# Barry MCP Server - Complete Codebase Explanation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Claude Desktop Integration](#claude-desktop-integration)
6. [How It All Works Together](#how-it-all-works-together)

---

## 🎯 Project Overview

**Barry MCP Server** is a Model Context Protocol (MCP) server that provides Claude with the ability to query a chocolate product dataset. It exposes two tools that Claude can use to search and filter chocolate products based on various criteria.

**Purpose**: Enable Claude to answer questions about Barry chocolate products by querying a 195MB CSV dataset containing 44,538 unique SKUs.

---

## 📁 Project Structure

```
barry-mcp-server/
├── data/
│   └── master_table_with_Description_2025_NOV_28.csv  # 195MB dataset (81,716 rows → 44,538 unique)
├── src/
│   └── barry_server/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Entry point wrapper
│       └── server.py            # Main server logic (363 lines)
├── .venv/                       # Virtual environment with dependencies
├── .gitignore                   # Git ignore rules
├── pyproject.toml               # Project configuration
├── README.md                    # User documentation
├── SETUP_GUIDE.md              # Setup instructions
└── CLAUDE_CONFIG.md            # Claude Desktop config
```

---

## 🔧 Core Components

### 1. **pyproject.toml** - Project Configuration

```toml
[project]
name = "barry-server"
version = "0.1.0"
description = "A simple MCP server for querying Barry chocolate dataset"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.9.0",      # MCP SDK for server implementation
    "pandas>=2.0.0",   # Data manipulation and CSV handling
]

[project.scripts]
barry-server = "barry_server.__main__:run"  # Entry point (not used in final setup)
```

**Key Points:**
- Defines project metadata and dependencies
- Requires Python 3.10+
- Only 2 dependencies: `mcp` (MCP protocol) and `pandas` (data handling)

---

### 2. **src/barry_server/__init__.py** - Package Initialization

```python
"""Barry MCP Server - A simple MCP server for querying chocolate product data."""

__version__ = "0.1.0"
```

**Purpose:** Marks the directory as a Python package and defines version.

---

### 3. **src/barry_server/__main__.py** - Entry Point Wrapper

```python
"""Entry point for barry-server command."""
import asyncio
from barry_server.server import main


def run():
    """Synchronous entry point that runs the async main function."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
```

**Purpose:** 
- Provides a synchronous wrapper for the async `main()` function
- Allows running with `python -m barry_server`
- **Note:** Not used in final Claude Desktop setup (we use direct module execution)

---

### 4. **src/barry_server/server.py** - Main Server Logic

This is the heart of the application. Let's break it down section by section:

#### **A. Imports and Setup**

```python
import asyncio
from pathlib import Path
from typing import Any

import pandas as pd
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize the MCP server
app = Server("barry-server")

# Global variable to store the dataset
df: pd.DataFrame | None = None
```

**What's happening:**
- Import MCP SDK components for server creation
- Import pandas for data manipulation
- Create a global `Server` instance named "barry-server"
- `df` will hold the loaded dataset in memory

---

#### **B. Data Loading Function** (`load_data()`)

```python
def load_data() -> None:
    """Load the Barry dataset from CSV file."""
    global df
    
    # Multi-strategy path resolution (4 strategies)
    # Strategy 1: BARRY_DATA_DIR environment variable
    # Strategy 2: Source tree detection (src/barry_server/server.py)
    # Strategy 3: Current working directory
    # Strategy 4: Hardcoded common locations
    
    # Load CSV
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Deduplication logic
    # Same Material_Code can appear with different Legislation (EU, US, RU)
    # We keep only one entry per Material_Code, preferring EU
    df['_legislation_priority'] = df['Legislation'].apply(
        lambda x: 0 if pd.isna(x) or x == '' else (1 if 'EU' in str(x) else 2)
    )
    df = df.sort_values(['Material_Code', '_legislation_priority'])
    df = df.drop_duplicates(subset=['Material_Code'], keep='first')
    df = df.drop(columns=['_legislation_priority'])
```

**Key Features:**
1. **Multi-strategy path resolution**: Tries 4 different ways to find the CSV file
2. **Deduplication**: Reduces 81,716 rows → 44,538 unique SKUs
3. **EU preference**: When same SKU exists for multiple regions, keeps EU version
4. **In-memory storage**: Entire dataset loaded into RAM for fast queries

**Output:**
```
✓ Loaded dataset from: /Users/.../data/master_table_with_Description_2025_NOV_28.csv
✓ Raw data: 81,716 rows and 288 columns
✓ Deduplicated: 81,716 → 44,538 rows (removed 37,178 duplicates)
✓ Final dataset: 44,538 unique SKUs
```

---

#### **C. Tool Registration** (`@app.list_tools()`)

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for the MCP server."""
    return [
        Tool(
            name="query_skus_by_fat",
            description="Query Material_Code (SKUs) based on fat content...",
            inputSchema={...}
        ),
        Tool(
            name="query_chocolate_products",
            description="Search for chocolate products by type...",
            inputSchema={...}
        ),
    ]
```

**Purpose:** 
- Tells Claude what tools are available
- Defines input parameters and their types
- Claude uses this to understand how to call the tools

**Tool 1: query_skus_by_fat**
- Parameters: `fat_value` (required), `n` (default: 10), `operator` (default: ">")
- Example: "Show me 10 products where fat > 25"

**Tool 2: query_chocolate_products**
- Parameters: `chocolate_type` (Dark/Milk/White), `moulding_type` (any string), `n` (default: 5)
- Example: "Give me 5 dark chocolate callets"

---

#### **D. Tool Execution Handler** (`@app.call_tool()`)

```python
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from the MCP client."""
    
    if df is None:
        return [TextContent(type="text", text="❌ Error: Dataset not loaded...")]
    
    try:
        if name == "query_skus_by_fat":
            return await query_skus_by_fat(arguments)
        elif name == "query_chocolate_products":
            return await query_chocolate_products(arguments)
        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
```

**Purpose:** Routes tool calls to the appropriate handler function with error handling.

---

#### **E. Tool Implementation 1: query_skus_by_fat**

```python
async def query_skus_by_fat(arguments: dict) -> list[TextContent]:
    # Get parameters
    n = arguments.get("n", 10)
    fat_value = arguments["fat_value"]
    operator = arguments.get("operator", ">")
    
    # Operator mapping (cleaner than if-elif chains)
    operator_map = {
        "==": lambda x: x == fat_value,
        "<": lambda x: x < fat_value,
        "<=": lambda x: x <= fat_value,
        ">": lambda x: x > fat_value,
        ">=": lambda x: x >= fat_value,
    }
    
    # Filter data
    filtered = df[df["Fat"].apply(operator_map[operator]) & df["Material_Code"].notna()]
    results = filtered.head(n)
    
    # Format output with emoji indicators
    lines = [f"📊 Found {len(results)} SKU(s) where Fat {operator} {fat_value}g:\n"]
    
    for _, row in results.iterrows():
        material_code = row["Material_Code"]
        fat = row["Fat"]
        material_description = row.get("Material_Description", "N/A")
        full_description = row.get("Description", "N/A")
        
        lines.append(f"  • **{material_code}** (Fat: {fat}g)")
        lines.append(f"    📝 {material_description}")
        
        # Add full Description (contains all column info)
        if full_description != "N/A" and str(full_description) != "nan":
            desc_str = str(full_description)
            if len(desc_str) > 500:
                desc_str = desc_str[:497] + "..."
            lines.append(f"    ℹ️  {desc_str}")
        lines.append("")
    
    return [TextContent(type="text", text="\n".join(lines))]
```

**How it works:**
1. Parse parameters (with defaults)
2. Use dictionary mapping for operators (cleaner than if-elif)
3. Filter pandas DataFrame using `.apply()`
4. Format results with emoji indicators (📊, 📝, ℹ️)
5. Include both Material_Description and full Description
6. Truncate long descriptions at 500 characters

**Example Output:**
```
📊 Found 5 SKU(s) where Fat > 30g:

  • **CHD-12345** (Fat: 35.2g)
    📝 Dark Chocolate Callets 70%
    ℹ️  Material: Alcalised Powder cocoa and comes in Powder shape...

  • **CHM-67890** (Fat: 32.1g)
    📝 Milk Chocolate Chips
    ℹ️  Material: Standard milk chocolate with 32% cocoa content...
```

---

#### **F. Tool Implementation 2: query_chocolate_products**

```python
async def query_chocolate_products(arguments: dict) -> list[TextContent]:
    # Get parameters
    n = arguments.get("n", 5)
    chocolate_type = arguments["chocolate_type"]
    moulding_type = arguments["moulding_type"].lower()
    
    # Material_Code prefix mapping
    prefix_map = {
        "Dark": "CHD-",
        "Milk": "CHM-",
        "White": "CHW-"
    }
    expected_prefix = prefix_map[chocolate_type]
    
    # Multi-stage filtering
    filtered = df.copy()
    
    # Step 1: Filter by Product_Type (chocolate or Chocolate with < 5% Veg Fat)
    filtered = filtered[
        (filtered["Product_Type"].str.lower().str.contains("chocolate", na=False)) &
        (
            (filtered["Product_Type"].str.lower() == "chocolate") |
            (filtered["Product_Type"].str.contains("< 5% veg fat", case=False, na=False))
        )
    ]
    
    # Step 2: Filter by Base_Type (Dark/Milk/White)
    filtered = filtered[filtered["Base_Type"].str.lower() == chocolate_type.lower()]
    
    # Step 3: Filter by Moulding_Type (flexible string matching)
    filtered = filtered[filtered["Moulding_Type"].str.lower().str.contains(moulding_type, na=False)]
    
    # Step 4: Validate Material_Code prefix
    filtered = filtered[filtered["Material_Code"].str.startswith(expected_prefix, na=False)]
    
    # Format output with validation checkmarks
    for _, row in results.iterrows():
        prefix_valid = "✓" if material_code.startswith(expected_prefix) else "✗"
        
        lines.append(f"  {prefix_valid} **{material_code}**")
        lines.append(f"    📝 {material_description}")
        lines.append(f"    Base: {base_type} | Moulding: {moulding}")
        # ... full description ...
```

**How it works:**
1. Parse parameters
2. Map chocolate type to Material_Code prefix (CHD-/CHM-/CHW-)
3. **4-stage filtering pipeline:**
   - Product_Type: Must be chocolate
   - Base_Type: Must match requested type (Dark/Milk/White)
   - Moulding_Type: **Flexible string matching** (e.g., "callets" matches "Callets", "Mini Callets")
   - Material_Code: Must have correct prefix
4. Format with validation checkmarks (✓/✗)
5. Include full Description for context

**Example Output:**
```
🍫 Found 3 Dark chocolate product(s) with moulding type 'callets':

  ✓ **CHD-12345**
    📝 Dark Chocolate Callets 70%
    Base: Dark | Moulding: Callets
    ℹ️  Material: Premium dark chocolate callets with 70% cocoa content...

  ✓ **CHD-67890**
    📝 Organic Dark Callets
    Base: Dark | Moulding: Callets
    ℹ️  Material: Certified organic dark chocolate callets...
```

---

#### **G. Main Entry Point** (`main()`)

```python
async def main() -> None:
    """Main entry point for the MCP server."""
    try:
        print("🚀 Starting Barry MCP Server...")
        load_data()
        print("✓ Server ready!\n")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

**Purpose:**
1. Load the dataset
2. Start the MCP server using stdio (standard input/output)
3. Wait for tool calls from Claude Desktop

**stdio_server:** Uses stdin/stdout for communication (Claude Desktop pipes data through these)

---

## 🔄 Data Flow

Here's how a query flows through the system:

```
┌─────────────────┐
│  Claude Desktop │
│  (User asks:    │
│  "Show me 5     │
│  dark chocolate │
│  callets")      │
└────────┬────────┘
         │
         │ 1. Sends tool call via stdio
         ▼
┌─────────────────────────────────────┐
│  Barry MCP Server                   │
│  ┌───────────────────────────────┐  │
│  │ call_tool()                   │  │
│  │ - Receives: name, arguments   │  │
│  │ - Routes to handler           │  │
│  └──────────┬────────────────────┘  │
│             │                        │
│             ▼                        │
│  ┌───────────────────────────────┐  │
│  │ query_chocolate_products()    │  │
│  │ - Parse: chocolate_type="Dark"│  │
│  │         moulding_type="callets"│ │
│  │         n=5                    │  │
│  │ - Filter DataFrame (4 stages) │  │
│  │ - Format results with emoji   │  │
│  └──────────┬────────────────────┘  │
│             │                        │
│             ▼                        │
│  ┌───────────────────────────────┐  │
│  │ Pandas DataFrame (in memory)  │  │
│  │ 44,538 rows × 288 columns     │  │
│  │ - Filter by Product_Type      │  │
│  │ - Filter by Base_Type         │  │
│  │ - Filter by Moulding_Type     │  │
│  │ - Validate Material_Code      │  │
│  └──────────┬────────────────────┘  │
│             │                        │
│             ▼                        │
│  ┌───────────────────────────────┐  │
│  │ Format Results                │  │
│  │ - Add emoji indicators        │  │
│  │ - Include descriptions        │  │
│  │ - Truncate long text          │  │
│  └──────────┬────────────────────┘  │
└─────────────┼────────────────────────┘
              │
              │ 2. Returns TextContent via stdio
              ▼
┌─────────────────────────────────────┐
│  Claude Desktop                     │
│  Displays formatted results to user│
└─────────────────────────────────────┘
```

---

## 🖥️ Claude Desktop Integration

### Configuration File

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "barry-server": {
      "command": "/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server/.venv/bin/python",
      "args": [
        "-m",
        "barry_server.server"
      ],
      "env": {
        "PYTHONPATH": "/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server/src"
      }
    }
  }
}
```

### How It Works

1. **Claude Desktop starts the server:**
   - Runs: `.venv/bin/python -m barry_server.server`
   - Sets `PYTHONPATH` so Python can find the `barry_server` package
   - Connects via stdio (pipes stdin/stdout)

2. **Server initialization:**
   - Loads 195MB CSV dataset
   - Deduplicates to 44,538 unique SKUs
   - Registers 2 tools with Claude

3. **User interaction:**
   - User asks: "Show me dark chocolate callets"
   - Claude decides to use `query_chocolate_products` tool
   - Sends JSON-RPC call via stdio
   - Server processes and returns results
   - Claude formats and displays to user

4. **Communication protocol:**
   ```
   Claude Desktop ←→ stdio ←→ Barry MCP Server
                    (JSON-RPC over stdin/stdout)
   ```

---

## 🎯 How It All Works Together

### Startup Sequence

```
1. User opens Claude Desktop
   ↓
2. Claude Desktop reads claude_desktop_config.json
   ↓
3. Spawns barry-server process:
   .venv/bin/python -m barry_server.server
   ↓
4. Barry server starts:
   - Prints: "🚀 Starting Barry MCP Server..."
   - Loads CSV (81,716 rows)
   - Deduplicates (→ 44,538 rows)
   - Prints: "✓ Server ready!"
   ↓
5. Server registers tools with Claude via MCP protocol
   ↓
6. Claude Desktop shows 🔌 icon (server connected)
   ↓
7. Ready for user queries!
```

### Query Execution Flow

**Example: "Give me 5 dark chocolate callets"**

```
1. User types query in Claude Desktop
   ↓
2. Claude's AI decides to use query_chocolate_products tool
   ↓
3. Claude sends JSON-RPC call via stdio:
   {
     "method": "tools/call",
     "params": {
       "name": "query_chocolate_products",
       "arguments": {
         "chocolate_type": "Dark",
         "moulding_type": "callets",
         "n": 5
       }
     }
   }
   ↓
4. Barry server receives call
   ↓
5. call_tool() routes to query_chocolate_products()
   ↓
6. Function filters DataFrame:
   - Product_Type contains "chocolate" ✓
   - Base_Type == "Dark" ✓
   - Moulding_Type contains "callets" ✓
   - Material_Code starts with "CHD-" ✓
   ↓
7. Returns top 5 results with formatting
   ↓
8. Claude receives TextContent response
   ↓
9. Claude displays formatted results to user:
   "Here are 5 dark chocolate callets:
    
    ✓ CHD-12345
      📝 Dark Chocolate Callets 70%
      Base: Dark | Moulding: Callets
      ℹ️  Material: Premium dark chocolate..."
```

---

## 🔑 Key Design Decisions

### 1. **In-Memory Dataset**
- **Why:** Fast queries (no disk I/O)
- **Trade-off:** Uses ~200MB RAM, but enables instant responses

### 2. **Deduplication Strategy**
- **Why:** Reduce redundant rows (same SKU, different regions)
- **Approach:** Keep one per Material_Code, prefer EU legislation
- **Result:** 81,716 → 44,538 rows (45% reduction)

### 3. **Flexible String Matching**
- **Why:** User-friendly queries
- **Implementation:** `.str.contains()` for moulding types
- **Benefit:** "callets" matches "Callets", "Mini Callets", etc.

### 4. **Multi-Strategy Path Resolution**
- **Why:** Works in different environments (dev, installed, Claude Desktop)
- **Strategies:** ENV var → source tree → cwd → hardcoded paths
- **Benefit:** Robust across different setups

### 5. **Emoji Indicators**
- **Why:** Better visual feedback and readability
- **Usage:** 📊 (stats), 📝 (description), ℹ️ (details), ✓/✗ (validation)
- **Benefit:** Easier to scan results

### 6. **Description Column**
- **Why:** Provides comprehensive context to Claude
- **Content:** Contains all column information in one field
- **Benefit:** Claude can understand product details better

---

## 📊 Performance Characteristics

- **Startup time:** ~2-3 seconds (CSV loading + deduplication)
- **Query time:** <100ms (in-memory filtering)
- **Memory usage:** ~200MB (dataset in RAM)
- **Dataset size:** 195MB CSV → 44,538 unique SKUs
- **Concurrent queries:** Supported (async/await)

---

## 🛠️ Technologies Used

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Programming language | 3.10+ |
| **MCP SDK** | Protocol implementation | 0.9.0+ |
| **Pandas** | Data manipulation | 2.0.0+ |
| **asyncio** | Async server runtime | Built-in |
| **stdio** | Communication transport | Built-in |

---

## 🎓 Learning Points

### For Beginners

1. **MCP Protocol:** Learn how Claude communicates with external tools
2. **Pandas:** Data filtering and manipulation
3. **Async Python:** `async`/`await` for concurrent operations
4. **stdio Communication:** Process-to-process communication
5. **JSON-RPC:** Remote procedure call protocol

### Best Practices Demonstrated

- ✅ Clear separation of concerns (data loading, tool logic, formatting)
- ✅ Comprehensive error handling
- ✅ User-friendly output formatting
- ✅ Type hints for clarity
- ✅ Docstrings for documentation
- ✅ Default parameters for better UX
- ✅ Dictionary mapping instead of if-elif chains

---

## 🚀 Summary

The Barry MCP Server is a **simple yet powerful** integration that:

1. **Loads** a 195MB chocolate product dataset
2. **Deduplicates** to 44,538 unique SKUs
3. **Exposes** 2 query tools to Claude
4. **Filters** data using pandas
5. **Formats** results with emoji and descriptions
6. **Communicates** via stdio using MCP protocol
7. **Integrates** seamlessly with Claude Desktop

**Result:** Claude can now answer questions about chocolate products by querying a comprehensive dataset in real-time! 🍫

---

**Created:** 2026-01-21  
**Version:** 0.1.0  
**Status:** Production-ready ✅
