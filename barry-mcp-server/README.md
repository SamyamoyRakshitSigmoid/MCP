# Barry MCP Server

A simple, beginner-friendly MCP (Model Context Protocol) server for querying chocolate product data from the Barry dataset.

## 🎯 Purpose

This server demonstrates how to build a basic MCP server in Python. It's designed to be easy to understand for newcomers to MCP development, with clear code comments and simple query tools.

## 🛠️ Features

The server provides two query tools:

### 1. Query SKUs by Fat Content
Filter products by fat content using comparison operators.

**Example queries:**
- "Give me 10 SKUs where fat is greater than 20"
- "Show me 5 products where fat is less than or equal to 15"

### 2. Query Chocolate Products
Search for chocolate products with specific characteristics (type, moulding).

**Example queries:**
- "Give me 5 dark chocolate callets"
- "Find 3 milk chocolate chips"

The tool automatically validates Material_Code prefixes:
- `CHD-` for Dark chocolate
- `CHM-` for Milk chocolate
- `CHW-` for White chocolate

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- The Barry dataset CSV file (included in `data/` directory)

### Install with uv (recommended)
```bash
cd barry-mcp-server
uv venv
uv pip install -e .
```

### Install with pip
```bash
cd barry-mcp-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## 🚀 Running the Server

### Standalone (for testing)
```bash
# With uv
uv run barry-server

# Or with activated venv
python -m barry_server.server
```

### With Claude Desktop

1. Open your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the server configuration:
```json
{
  "mcpServers": {
    "barry-server": {
      "command": "uv",
      "args": [
        "--directory",
        "MCP/barry-mcp-server",
        "run",
        "barry-server"
      ]
    }
  }
}
```

3. Restart Claude Desktop

4. Look for the 🔌 icon to verify the server is connected

## 💡 Usage Examples

Once configured in Claude Desktop, you can ask:

### Fat Content Queries
```
"Show me 10 products where fat is greater than 25 grams"
"Find 5 SKUs with fat less than 10 grams"
"List products where fat equals 21 grams"
```

### Chocolate Product Queries
```
"Give me 5 dark chocolate callets"
"Find 3 milk chocolate chips"
"Show me 10 white chocolate blocks"
```

## 📁 Project Structure

```
barry-mcp-server/
├── data/
│   └── master_table_with_Description_2025_NOV_28.csv  # Dataset (195MB)
├── src/
│   └── barry_server/
│       ├── __init__.py          # Package initialization
│       └── server.py            # Main server implementation (280 lines)
├── .venv/                       # Virtual environment
├── .gitignore                   # Git ignore file
├── pyproject.toml               # Project configuration
├── README.md                    # This file
└── SETUP_GUIDE.md              # Detailed setup instructions
```

## 🔍 How It Works

### Tool 1: query_skus_by_fat
1. Takes parameters: `fat_value` (required), `n` (default: 10), `operator` (default: ">")
2. Filters the dataset based on the Fat column
3. Returns up to `n` Material_Code entries with their fat content
4. Output includes emoji indicators and formatted data

### Tool 2: query_chocolate_products
1. Takes parameters: `chocolate_type` (Dark/Milk/White), `moulding_type` (e.g., "callets"), `n` (default: 5)
2. Filters by:
   - Product_Type = "chocolate" or "Chocolate with < 5% Veg Fat"
   - Base_Type matches the specified chocolate type
   - Moulding_Type contains the specified moulding type
3. Validates Material_Code prefix (CHD-/CHM-/CHW-)
4. Returns up to `n` matching products with validation checkmarks

## ✨ Recent Improvements

- 🎨 **Emoji indicators** for better visual feedback (✓, ❌, 🔍, 🍫, 📊)
- 📝 **Auto-truncated descriptions** to prevent overwhelming output
- 🎯 **Default parameters** for easier queries
- 🛡️ **Better error handling** with clear, actionable messages
- 📊 **Formatted numbers** with comma separators
- 🔧 **Cleaner code** using dictionary mapping instead of if-elif chains

## 🐛 Troubleshooting

### Server not appearing in Claude Desktop
- Check that the path in `claude_desktop_config.json` is correct
- Restart Claude Desktop completely
- Check the Claude Desktop logs for errors

### "Dataset not found" error
- Verify the CSV file exists at: `data/master_table_with_Description_2025_NOV_28.csv`
- The file should be ~195MB in size

### No results returned
- The dataset might not have products matching your criteria
- Try broader search terms (e.g., "choc" instead of "chocolate")
- Try different fat thresholds or chocolate types

## 📚 Learning Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Building MCP Servers](https://modelcontextprotocol.io/docs/building-servers)

## 📝 License

This is a sample project for educational purposes.

---

**Made with ❤️ for learning MCP development**
