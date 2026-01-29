"""
MCP Client for connecting to Barry server.

This module handles the connection to the Barry MCP server and provides
methods to list tools and execute tool calls.
"""

import asyncio
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class BarryMCPClient:
    """Client for connecting to Barry MCP server."""
    
    def __init__(self, server_path: str, server_python: str):
        """
        Initialize the Barry MCP client.
        
        Args:
            server_path: Path to the barry-mcp-server directory
            server_python: Path to Python executable (venv python)
        """
        self.server_path = Path(server_path)
        self.server_python = server_python
        self.session: ClientSession | None = None
        self.tools = []
        self.read_stream = None
        self.write_stream = None
        
    async def connect(self):
        """Connect to the Barry MCP server."""
        print("  → Setting up server parameters...")
        # Set up server parameters
        server_params = StdioServerParameters(
            command=self.server_python,
            args=["-m", "barry_server.server"],
            env={
                "PYTHONPATH": str(self.server_path / "src")
            }
        )
        
        print(f"  → Connecting to server: {self.server_python}")
        print(f"  → Server path: {self.server_path}")
        
        # Connect to server using async context manager properly
        # Store the context manager for later cleanup
        self.stdio_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.stdio_context.__aenter__()
        print("  → Server process started")
        
        # Create session
        print("  → Creating MCP session...")
        self.session = ClientSession(self.read_stream, self.write_stream)
        
        # Start the session (this runs in background)
        print("  → Starting session...")
        await self.session.__aenter__()
        
        # Initialize session
        print("  → Initializing session...")
        try:
            init_result = await asyncio.wait_for(
                self.session.initialize(),
                timeout=10.0
            )
            print(f"  → Session initialized: {init_result.serverInfo.name}")
        except asyncio.TimeoutError:
            print("❌ Timeout: Session initialization took too long")
            print("   The Barry server may not be responding properly")
            raise
        
        # List available tools
        print("  → Listing tools...")
        response = await self.session.list_tools()
        self.tools = response.tools
        
        print(f"✓ Connected to Barry MCP Server")
        print(f"✓ Available tools: {len(self.tools)}")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description}")
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        Call a tool on the Barry MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result as string
        """
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect() first.")
        
        # Execute tool call
        result = await self.session.call_tool(tool_name, arguments)
        
        # Extract text content from result
        if result.content:
            return "\n".join(
                item.text for item in result.content 
                if hasattr(item, 'text')
            )
        return "No result"
    
    async def disconnect(self):
        """Disconnect from the Barry MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_context'):
            await self.stdio_context.__aexit__(None, None, None)
        print("✓ Disconnected from Barry MCP Server")
    
    def get_tools_schema(self) -> list[dict]:
        """
        Get tools in Gemini function calling format.
        
        Returns:
            List of tool schemas for Gemini
        """
        gemini_tools = []
        
        for tool in self.tools:
            # Convert MCP tool schema to Gemini format
            gemini_tool = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
            gemini_tools.append(gemini_tool)
        
        return gemini_tools
