"""
Ollama Agent with MCP tool integration.

This module integrates Ollama (open-source models) with the Barry MCP client,
allowing local LLMs to use MCP tools for querying chocolate product data.
"""

import asyncio
import json
import os
from typing import Any

import ollama
from dotenv import load_dotenv

from barry_client.client import BarryMCPClient


class OllamaAgent:
    """Ollama agent with MCP tool integration."""
    
    def __init__(self, model: str, mcp_client: BarryMCPClient, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama agent.
        
        Args:
            model: Ollama model name (e.g., 'qwen2.5-coder:7b', 'llama3.1')
            mcp_client: Connected Barry MCP client
            base_url: Ollama server URL
        """
        self.model = model
        self.mcp_client = mcp_client
        self.base_url = base_url
        
        # Initialize Ollama client
        self.client = ollama.Client(host=base_url)
        
        # Get tools from MCP client and convert to Ollama format
        tools_schema = mcp_client.get_tools_schema()
        self.tools = self._convert_tools_to_ollama(tools_schema)
        
        # Conversation history
        self.messages = []
        
        print(f"✓ Initialized Ollama ({model}) with {len(self.tools)} tools")
    
    def _convert_tools_to_ollama(self, tools_schema: list[dict]) -> list[dict]:
        """Convert MCP tool schemas to Ollama function format."""
        ollama_tools = []
        
        for tool in tools_schema:
            # Ollama uses a simpler format - just pass through the schema
            ollama_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            ollama_tools.append(ollama_tool)
        
        return ollama_tools
    
    async def send_message(self, message: str) -> str:
        """
        Send a message to Ollama and handle tool calls.
        
        Args:
            message: User message
            
        Returns:
            Ollama's response
        """
        print(f"\n💬 You: {message}")
        
        # Add user message to history
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
        
        # Handle tool calls in a loop
        while response.get('message', {}).get('tool_calls'):
            # Add assistant's response with tool calls to history
            self.messages.append(response['message'])
            
            # Process each tool call
            for tool_call in response['message']['tool_calls']:
                function_name = tool_call['function']['name']
                function_args = tool_call['function']['arguments']
                
                print(f"\n🔧 Ollama calling tool: {function_name}")
                print(f"   Arguments: {function_args}")
                
                # Execute the function call via MCP
                try:
                    result = await self.mcp_client.call_tool(
                        function_name,
                        function_args
                    )
                    
                    print(f"✓ Tool result received ({len(result)} chars)")
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "content": result
                    })
                    
                except Exception as e:
                    print(f"❌ Error calling tool: {e}")
                    # Add error to messages
                    self.messages.append({
                        "role": "tool",
                        "content": f"Error: {str(e)}"
                    })
            
            # Continue conversation with tool results
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self.tools
            )
        
        # Add final response to history
        self.messages.append(response['message'])
        
        # Get final text response
        final_response = response['message']['content']
        print(f"\n🤖 Ollama: {final_response}")
        
        return final_response


async def main():
    """Main entry point for Ollama agent."""
    # Load environment variables
    load_dotenv()
    
    model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    server_path = os.getenv("BARRY_SERVER_PATH")
    server_python = os.getenv("BARRY_SERVER_PYTHON")
    
    if not server_path or not server_python:
        print("❌ Error: BARRY_SERVER_PATH or BARRY_SERVER_PYTHON not set in .env file")
        return
    
    # Check if Ollama is running
    try:
        client = ollama.Client(host=base_url)
        client.list()
        print(f"✓ Connected to Ollama at {base_url}")
    except Exception as e:
        print(f"❌ Error: Could not connect to Ollama at {base_url}")
        print(f"   Make sure Ollama is running: ollama serve")
        print(f"   Error: {e}")
        return
    
    # Check if model is available
    try:
        models = client.list()
        # Ollama returns 'model' key, not 'name'
        model_names = [m.get('model', m.get('name', '')) for m in models.get('models', [])]
        if model not in model_names:
            print(f"⚠️  Model '{model}' not found locally.")
            print(f"   Available models: {', '.join(model_names)}")
            print(f"\n   To pull the model, run: ollama pull {model}")
            return
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        print(f"   Debug - models response: {models}")
        return
    
    # Create and connect MCP client
    print(f"\n🚀 Starting Barry MCP Client...")
    mcp_client = BarryMCPClient(server_path, server_python)
    
    try:
        await mcp_client.connect()
        
        # Create Ollama agent
        print(f"\n🤖 Initializing Ollama Agent...")
        agent = OllamaAgent(model, mcp_client, base_url)
        
        print("\n" + "="*60)
        print(f"Barry MCP Client with Ollama ({model}) - Ready!")
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
                
                # Send message to Ollama
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
