"""
Gemini Agent with MCP tool integration.

This module integrates Google's Gemini API with the Barry MCP client,
allowing Gemini to use MCP tools for querying chocolate product data.
"""

import asyncio
import json
import os
from typing import Any

from google import genai
from google.genai import types
from dotenv import load_dotenv

from barry_client.client import BarryMCPClient


class GeminiAgent:
    """Gemini agent with MCP tool integration."""
    
    def __init__(self, api_key: str, mcp_client: BarryMCPClient):
        """
        Initialize Gemini agent.
        
        Args:
            api_key: Gemini API key
            mcp_client: Connected Barry MCP client
        """
        self.api_key = api_key
        self.mcp_client = mcp_client
        
        # Create Gemini client
        self.client = genai.Client(api_key=api_key)
        
        # Get tools from MCP client and convert to Gemini format
        tools_schema = mcp_client.get_tools_schema()
        self.function_declarations = self._convert_tools_to_gemini(tools_schema)
        
        print(f"✓ Initialized Gemini with {len(self.function_declarations)} tools")
    
    def _convert_tools_to_gemini(self, tools_schema: list[dict]) -> list[types.FunctionDeclaration]:
        """Convert MCP tool schemas to Gemini function declarations."""
        function_declarations = []
        
        for tool in tools_schema:
            # Convert properties
            properties = {}
            for prop_name, prop_schema in tool["parameters"].get("properties", {}).items():
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
    
    async def send_message(self, message: str) -> str:
        """
        Send a message to Gemini and handle tool calls.
        
        Args:
            message: User message
            
        Returns:
            Gemini's response
        """
        print(f"\n💬 You: {message}")
        
        # Create chat with tools
        chat = self.client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=self.function_declarations)],
                temperature=0.7
            )
        )
        
        # Send initial message
        response = chat.send_message(message)
        
        # Handle function calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # Check if it's a function call
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                
                print(f"\n🔧 Gemini calling tool: {function_call.name}")
                print(f"   Arguments: {dict(function_call.args)}")
                
                # Execute the function call via MCP
                try:
                    result = await self.mcp_client.call_tool(
                        function_call.name,
                        dict(function_call.args)
                    )
                    
                    print(f"✓ Tool result received ({len(result)} chars)")
                    
                    # Send function response back to Gemini
                    # Include the result in a way that Gemini will use it
                    response = chat.send_message(
                        f"Here is the data from the {function_call.name} function:\n\n{result}\n\nPlease format this nicely for the user."
                    )
                except Exception as e:
                    print(f"❌ Error calling tool: {e}")
                    # Send error back to Gemini as a string
                    response = chat.send_message(
                        f"Error calling function {function_call.name}: {str(e)}"
                    )
            else:
                # No more function calls, break
                break
        
        # Get final text response
        final_response = response.text if hasattr(response, 'text') else str(response)
        print(f"\n🤖 Gemini: {final_response}")
        
        return final_response


async def main():
    """Main entry point for Gemini agent."""
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    server_path = os.getenv("BARRY_SERVER_PATH")
    server_python = os.getenv("BARRY_SERVER_PYTHON")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not set in .env file")
        return
    
    if not server_path or not server_python:
        print("❌ Error: BARRY_SERVER_PATH or BARRY_SERVER_PYTHON not set in .env file")
        return
    
    # Create and connect MCP client
    print("🚀 Starting Barry MCP Client...")
    mcp_client = BarryMCPClient(server_path, server_python)
    
    try:
        await mcp_client.connect()
        
        # Create Gemini agent
        print("\n🤖 Initializing Gemini Agent...")
        agent = GeminiAgent(api_key, mcp_client)
        
        print("\n" + "="*60)
        print("Barry MCP Client with Gemini - Ready!")
        print("="*60)
        print("\nYou can now ask questions about chocolate products.")
        print("Examples:")
        print("  - Show me 10 products where fat is greater than 30")
        print("  - Give me 5 dark chocolate callets")
        print("  - Find milk chocolate chips")
        print("\nType 'quit' or 'exit' to stop.\n")
        
        # Conversation loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Send message to Gemini
                await agent.send_message(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    finally:
        # Disconnect from MCP server
        await mcp_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
