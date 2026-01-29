#!/usr/bin/env python3
"""
Barry MCP Server - A beginner-friendly MCP server for querying chocolate product data.

This server provides two simple tools:
1. query_skus_by_fat: Filter products by fat content
2. query_chocolate_products: Search for chocolate products with specific characteristics
"""

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


def load_data() -> None:
    """Load the Barry dataset from CSV file."""
    global df
    
    # Try multiple strategies to find the data file
    csv_filename = "master_table_with_Description_2025_NOV_28.csv"
    csv_path = None
    
    # Strategy 1: Use BARRY_DATA_DIR environment variable if set
    import os
    if "BARRY_DATA_DIR" in os.environ:
        csv_path = Path(os.environ["BARRY_DATA_DIR"]) / csv_filename
    
    # Strategy 2: Look in the project directory (for development)
    if csv_path is None or not csv_path.exists():
        # Get the actual source file location (not the installed location)
        source_file = Path(__file__)
        # Check if we're in the source tree (src/barry_server/server.py)
        if source_file.parts[-3:-1] == ('src', 'barry_server'):
            project_root = source_file.parent.parent.parent
            csv_path = project_root / "data" / csv_filename
    
    # Strategy 3: Look relative to current working directory
    if csv_path is None or not csv_path.exists():
        cwd_path = Path.cwd() / "data" / csv_filename
        if cwd_path.exists():
            csv_path = cwd_path
    
    # Strategy 4: Look in common locations
    if csv_path is None or not csv_path.exists():
        possible_locations = [
            Path("/Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server/data") / csv_filename,
            Path.home() / "Documents" / "MCP Servers" / "barry-mcp-server" / "data" / csv_filename,
        ]
        for loc in possible_locations:
            if loc.exists():
                csv_path = loc
                break
    
    if csv_path is None or not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found. Tried:\n"
            f"  1. BARRY_DATA_DIR environment variable\n"
            f"  2. Project source tree: {source_file.parent.parent.parent / 'data' / csv_filename}\n"
            f"  3. Current directory: {Path.cwd() / 'data' / csv_filename}\n"
            f"  4. Default location: /Users/samyamoyrakshit/Documents/MCP Servers/barry-mcp-server/data/{csv_filename}\n"
            f"\nPlease ensure the CSV file exists in one of these locations."
        )
    
    # Load the CSV file
    import sys
    df = pd.read_csv(csv_path, low_memory=False)
    # print(f"✓ Loaded dataset from: {csv_path}")
    # print(f"✓ Raw data: {len(df):,} rows and {len(df.columns)} columns")
    print(f"✓ Loaded dataset from: {csv_path}", file=sys.stderr)
    print(f"✓ Raw data: {len(df):,} rows and {len(df.columns)} columns", file=sys.stderr)
    
    # Deduplicate based on Material_Code to reduce redundant rows
    # Same Material_Code can appear with different Legislation (EU, US, RU, etc.)
    # We'll keep only one entry per Material_Code, preferring EU legislation
    original_count = len(df)
    
    # Sort by Material_Code and Legislation, putting EU first
    df['_legislation_priority'] = df['Legislation'].apply(
        lambda x: 0 if pd.isna(x) or x == '' else (1 if 'EU' in str(x) else 2)
    )
    df = df.sort_values(['Material_Code', '_legislation_priority'])
    
    # Keep first occurrence of each Material_Code (which will be EU if available)
    df = df.drop_duplicates(subset=['Material_Code'], keep='first')
    df = df.drop(columns=['_legislation_priority'])
    
    deduplicated_count = len(df)
    # print(f"✓ Deduplicated: {original_count:,} → {deduplicated_count:,} rows (removed {original_count - deduplicated_count:,} duplicates)")
    # print(f"✓ Final dataset: {deduplicated_count:,} unique SKUs")
    
    print(f"✓ Deduplicated: {original_count:,} → {deduplicated_count:,} rows (removed {original_count - deduplicated_count:,} duplicates)", file=sys.stderr)
    print(f"✓ Final dataset: {deduplicated_count:,} unique SKUs", file=sys.stderr)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for the MCP server."""
    return [
        Tool(
            name="query_skus_by_fat",
            description="Query Material_Code (SKUs) based on fat content with comparison operators (==, <, <=, >, >=)",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "minimum": 1,
                        "default": 10,
                    },
                    "fat_value": {
                        "type": "number",
                        "description": "Fat content threshold value (in grams)",
                    },
                    "operator": {
                        "type": "string",
                        "description": "Comparison operator to use",
                        "enum": ["==", "<", "<=", ">", ">="],
                        "default": ">",
                    },
                },
                "required": ["fat_value"],
            },
        ),
        Tool(
            name="query_chocolate_products",
            description="Search for chocolate products by type (Dark/Milk/White) and moulding type (e.g., callets). Validates Material_Code prefix.",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "minimum": 1,
                        "default": 5,
                    },
                    "chocolate_type": {
                        "type": "string",
                        "description": "Type of chocolate base",
                        "enum": ["Dark", "Milk", "White"],
                    },
                    "moulding_type": {
                        "type": "string",
                        "description": "Moulding type to search for - uses flexible string matching (e.g., 'callets', 'chips', 'blocks', 'drops', 'bars', etc.)",
                    },
                },
                "required": ["chocolate_type", "moulding_type"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from the MCP client."""
    
    if df is None:
        return [TextContent(type="text", text="❌ Error: Dataset not loaded. Please restart the server.")]
    
    try:
        if name == "query_skus_by_fat":
            return await query_skus_by_fat(arguments)
        elif name == "query_chocolate_products":
            return await query_chocolate_products(arguments)
        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def query_skus_by_fat(arguments: dict) -> list[TextContent]:
    """
    Tool 1: Query SKUs by fat content.
    
    Filters Material_Code entries based on fat content using comparison operators.
    
    Args:
        arguments: Dict with 'n', 'fat_value', and 'operator'
    
    Returns:
        List of TextContent with formatted results
    """
    # Get parameters with defaults
    n = arguments.get("n", 10)
    fat_value = arguments["fat_value"]
    operator = arguments.get("operator", ">")
    
    # Validate Fat column exists
    if "Fat" not in df.columns:
        return [TextContent(type="text", text="❌ Error: 'Fat' column not found in dataset")]
    
    # Apply filter based on operator
    operator_map = {
        "==": lambda x: x == fat_value,
        "<": lambda x: x < fat_value,
        "<=": lambda x: x <= fat_value,
        ">": lambda x: x > fat_value,
        ">=": lambda x: x >= fat_value,
    }
    
    if operator not in operator_map:
        return [TextContent(type="text", text=f"❌ Invalid operator: {operator}")]
    
    # Filter data
    filtered = df[df["Fat"].apply(operator_map[operator]) & df["Material_Code"].notna()].copy()
    
    # Limit results
    results = filtered.head(n)
    
    if len(results) == 0:
        return [TextContent(
            type="text",
            text=f"🔍 No SKUs found where Fat {operator} {fat_value}g"
        )]
    
    # Format output
    lines = [f"📊 Found {len(results)} SKU(s) where Fat {operator} {fat_value}g:\n"]
    
    for _, row in results.iterrows():
        material_code = row["Material_Code"]
        fat = row["Fat"]
        material_description = row.get("Material_Description", "N/A")
        full_description = row.get("Description", "N/A")
        
        lines.append(f"  • **{material_code}** (Fat: {fat}g)")
        lines.append(f"    📝 {material_description}")
        
        # Add full Description if available (contains all column info)
        if full_description != "N/A" and str(full_description) != "nan":
            # Truncate if too long but keep it readable
            desc_str = str(full_description)
            if len(desc_str) > 500:
                desc_str = desc_str[:497] + "..."
            lines.append(f"    ℹ️  {desc_str}")
        lines.append("")
    
    return [TextContent(type="text", text="\n".join(lines))]


async def query_chocolate_products(arguments: dict) -> list[TextContent]:
    """
    Tool 2: Query chocolate products with filters.
    
    Filters by Product_Type, Base_Type, Moulding_Type, and validates Material_Code prefix.
    
    Args:
        arguments: Dict with 'n', 'chocolate_type', and 'moulding_type'
    
    Returns:
        List of TextContent with formatted results
    """
    # Get parameters with defaults
    n = arguments.get("n", 5)
    chocolate_type = arguments["chocolate_type"]
    moulding_type = arguments["moulding_type"].lower()
    
    # Validate required columns
    required_cols = ["Product_Type", "Base_Type", "Moulding_Type", "Material_Code"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        return [TextContent(
            type="text",
            text=f"❌ Missing columns: {', '.join(missing_cols)}"
        )]
    
    # Define Material_Code prefix mapping
    prefix_map = {
        "Dark": "CHD-",
        "Milk": "CHM-",
        "White": "CHW-"
    }
    expected_prefix = prefix_map[chocolate_type]
    
    # Apply filters step by step
    filtered = df.copy()
    
    # Step 1: Filter by Product_Type (chocolate or Chocolate with < 5% Veg Fat)
    filtered = filtered[
        (filtered["Product_Type"].str.lower().str.contains("chocolate", na=False)) &
        (
            (filtered["Product_Type"].str.lower() == "chocolate") |
            (filtered["Product_Type"].str.contains("< 5% veg fat", case=False, na=False))
        )
    ]
    
    # Step 2: Filter by Base_Type
    filtered = filtered[filtered["Base_Type"].str.lower() == chocolate_type.lower()]
    
    # Step 3: Filter by Moulding_Type (contains search term)
    filtered = filtered[filtered["Moulding_Type"].str.lower().str.contains(moulding_type, na=False)]
    
    # Step 4: Validate Material_Code prefix
    filtered = filtered[filtered["Material_Code"].str.startswith(expected_prefix, na=False)]
    
    # Limit results
    results = filtered.head(n)
    
    if len(results) == 0:
        return [TextContent(
            type="text",
            text=f"🔍 No {chocolate_type} chocolate products found with moulding type '{moulding_type}'"
        )]
    
    # Format output
    lines = [
        f"🍫 Found {len(results)} {chocolate_type} chocolate product(s) with moulding type '{moulding_type}':\n"
    ]
    
    for _, row in results.iterrows():
        material_code = row["Material_Code"]
        material_description = row.get("Material_Description", "N/A")
        base_type = row.get("Base_Type", "N/A")
        moulding = row.get("Moulding_Type", "N/A")
        full_description = row.get("Description", "N/A")
        
        # Validation check
        prefix_valid = "✓" if material_code.startswith(expected_prefix) else "✗"
        
        lines.append(f"  {prefix_valid} **{material_code}**")
        lines.append(f"    📝 {material_description}")
        lines.append(f"    Base: {base_type} | Moulding: {moulding}")
        
        # Add full Description if available (contains all column info)
        if full_description != "N/A" and str(full_description) != "nan":
            # Truncate if too long but keep it readable
            desc_str = str(full_description)
            if len(desc_str) > 500:
                desc_str = desc_str[:497] + "..."
            lines.append(f"    ℹ️  {desc_str}")
        lines.append("")
    
    return [TextContent(type="text", text="\n".join(lines))]


async def main() -> None:
    """Main entry point for the MCP server."""
    import sys
    try:
        print("🚀 Starting Barry MCP Server...", file=sys.stderr)
        load_data()
        print("✓ Server ready!\n", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error loading data: {e}", file=sys.stderr)
        return
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )
if __name__ == "__main__":
    asyncio.run(main())
