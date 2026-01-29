# Barry MCP Server - Setup Guide

## Quick Start Guide

This guide will help you set up and run the Barry MCP Server step by step.

---

## Step 1: Verify Prerequisites

Make sure you have:
- ✅ Python 3.10 or higher installed
- ✅ The Barry dataset CSV file at: `/Users/samyamoyrakshit/Documents/MCP Servers/barry-server/master_table_with_Description_2025_NOV_28.csv`

---

## Step 2: Install the Server

Open your terminal and run:

```bash
cd "/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server"
uv venv
uv pip install -e .
```

You should see output confirming the installation of `barry-server==0.1.0` and its dependencies.

---

## Step 3: Test the Server (Optional)

To verify the server works, run:

```bash
python -m barry_server.server
```

The server should start and display:
```
✓ Loaded dataset with XXXXX rows and XXX columns
```

Press `Ctrl+C` to stop the server.

---

## Step 4: Configure Claude Desktop

### 4.1 Open Claude Desktop Config

Open the configuration file in your text editor:

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 4.2 Add Server Configuration

Add the following to your `mcpServers` section:

```json
{
  "mcpServers": {
    "barry-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server",
        "run",
        "barry-server"
      ]
    }
  }
}
```

**Complete example** (if you have other servers):
```json
{
  "mcpServers": {
    "cricket-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/samyamoyrakshit/Documents/MCP Servers/cricket-server",
        "run",
        "cricket-server"
      ]
    },
    "barry-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server",
        "run",
        "barry-server"
      ]
    }
  }
}
```

### 4.3 Restart Claude Desktop

Completely quit and restart Claude Desktop for the changes to take effect.

---

## Step 5: Verify Connection

After restarting Claude Desktop:

1. Look for the **🔌 icon** in the bottom-right corner
2. Click it to see connected MCP servers
3. You should see **"barry-server"** listed
4. The status should show as **connected**

---

## Step 6: Try It Out!

Ask Claude queries like:

### Query 1: Fat Content Search
```
"Show me 10 products where fat is greater than 25 grams"
```

### Query 2: Chocolate Product Search
```
"Give me 5 dark chocolate callets"
```

---

## 🎉 You're All Set!

Your Barry MCP Server is now running and ready to query chocolate product data!

---

## 🐛 Troubleshooting

### Server not showing in Claude Desktop

**Problem:** Barry-server doesn't appear in the MCP servers list

**Solutions:**
1. Check the path in `claude_desktop_config.json` is correct
2. Make sure you completely quit and restarted Claude Desktop (not just closed the window)
3. Check Claude Desktop logs:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### Dataset not found error

**Problem:** Error message says "Dataset not found"

**Solutions:**
1. Verify the CSV file exists:
   ```bash
   ls -la "/Users/samyamoyrakshit/Documents/MCP Servers/barry-server/master_table_with_Description_2025_NOV_28.csv"
   ```
2. If the file is in a different location, update the path in `src/barry_server/server.py` line 25

### No results returned

**Problem:** Queries return "No SKUs found" or "No products found"

**Solutions:**
1. Try broader search criteria (e.g., lower fat threshold)
2. Check if the column names match (Fat, Product_Type, Base_Type, Moulding_Type)
3. Try different chocolate types or moulding types

### Installation errors

**Problem:** `uv pip install -e .` fails

**Solutions:**
1. Make sure you created the virtual environment first:
   ```bash
   uv venv
   ```
2. Try using pip instead:
   ```bash
   source .venv/bin/activate
   pip install -e .
   ```

---

## 📚 Available Tools

### 1. query_skus_by_fat

**Purpose:** Find products by fat content

**Parameters:**
- `n`: Number of results (e.g., 5, 10)
- `fat_value`: Fat threshold (e.g., 20, 15.5)
- `operator`: Comparison operator (`==`, `<`, `<=`, `>`, `>=`)

**Example:**
```
"Find 10 SKUs where fat is less than 15 grams"
```

### 2. query_chocolate_products

**Purpose:** Search for chocolate products

**Parameters:**
- `n`: Number of results (e.g., 5, 10)
- `chocolate_type`: Type of chocolate (`Dark`, `Milk`, `White`)
- `moulding_type`: Moulding form (e.g., `callets`, `chips`, `blocks`)

**Example:**
```
"Show me 5 milk chocolate chips"
```

**Material Code Validation:**
- Dark chocolate: `CHD-` prefix
- Milk chocolate: `CHM-` prefix
- White chocolate: `CHW-` prefix

---

## 🔄 Updating the Server

If you make changes to the server code:

1. The changes are automatically reflected (editable install with `-e`)
2. Restart Claude Desktop to reload the server
3. No need to reinstall unless you change dependencies

---

## 📖 Next Steps

- Explore the dataset to understand available columns
- Try different query combinations
- Modify the server code to add new tools
- Check out the [MCP Documentation](https://modelcontextprotocol.io/) to learn more

---

**Happy querying! 🍫**
