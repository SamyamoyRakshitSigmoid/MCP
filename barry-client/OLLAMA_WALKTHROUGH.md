# Ollama vs Gemini: Code Comparison Walkthrough

This document compares the Ollama and Gemini implementations for the Barry MCP Client, highlighting the simplicity advantages of using open-source models with Ollama.

## Executive Summary

**Key Metrics:**
- **Ollama**: ~180 lines of code
- **Gemini**: ~204 lines of code
- **Reduction**: ~12% less code with Ollama
- **Complexity**: Significantly simpler API with Ollama

## Code Comparison

### 1. Initialization

#### Gemini (Complex Type System)
```python
from google import genai
from google.genai import types

class GeminiAgent:
    def __init__(self, api_key: str, mcp_client: BarryMCPClient):
        self.client = genai.Client(api_key=api_key)
        
        # Complex type conversion required
        tools_schema = mcp_client.get_tools_schema()
        self.function_declarations = self._convert_tools_to_gemini(tools_schema)
```

#### Ollama (Simple Dictionary Format)
```python
import ollama

class OllamaAgent:
    def __init__(self, model: str, mcp_client: BarryMCPClient, base_url: str = "http://localhost:11434"):
        self.client = ollama.Client(host=base_url)
        
        # Simple dictionary format - no complex conversions
        tools_schema = mcp_client.get_tools_schema()
        self.tools = self._convert_tools_to_ollama(tools_schema)
```

**Winner: Ollama** ✅ - No API key needed, simpler initialization

---

### 2. Tool Schema Conversion

#### Gemini (30+ lines, complex type mapping)
```python
def _convert_tools_to_gemini(self, tools_schema: list[dict]) -> list[types.FunctionDeclaration]:
    function_declarations = []
    
    for tool in tools_schema:
        # Convert properties with type mapping
        properties = {}
        for prop_name, prop_schema in tool["parameters"].get("properties", {}).items():
            prop_type = prop_schema.get("type", "string").upper()
            properties[prop_name] = types.Schema(
                type=types.Type[prop_type],
                description=prop_schema.get("description", ""),
                enum=prop_schema.get("enum") if prop_schema.get("enum") else None
            )
        
        # Create function declaration with complex types
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

#### Ollama (10 lines, simple pass-through)
```python
def _convert_tools_to_ollama(self, tools_schema: list[dict]) -> list[dict]:
    ollama_tools = []
    
    for tool in tools_schema:
        # Simple wrapper - Ollama accepts standard JSON schema
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
```

**Winner: Ollama** ✅ - 70% less code, no type gymnastics

---

### 3. Chat Initialization

#### Gemini (Separate chat creation)
```python
async def send_message(self, message: str) -> str:
    # Create new chat each time
    chat = self.client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=self.function_declarations)],
            temperature=0.7
        )
    )
    
    response = chat.send_message(message)
```

#### Ollama (Direct chat with message history)
```python
async def send_message(self, message: str) -> str:
    # Add to message history
    self.messages.append({
        "role": "user",
        "content": message
    })
    
    # Simple chat call
    response = self.client.chat(
        model=self.model,
        messages=self.messages,
        tools=self.tools
    )
```

**Winner: Ollama** ✅ - Simpler API, built-in message history

---

### 4. Tool Call Handling

#### Gemini (Complex response parsing)
```python
while response.candidates[0].content.parts:
    part = response.candidates[0].content.parts[0]
    
    if hasattr(part, 'function_call') and part.function_call:
        function_call = part.function_call
        
        result = await self.mcp_client.call_tool(
            function_call.name,
            dict(function_call.args)  # Convert from special type
        )
        
        # Send result back as a new message (workaround)
        response = chat.send_message(
            f"Here is the data from the {function_call.name} function:\\n\\n{result}\\n\\nPlease format this nicely for the user."
        )
```

#### Ollama (Clean, standard format)
```python
while response.get('message', {}).get('tool_calls'):
    self.messages.append(response['message'])
    
    for tool_call in response['message']['tool_calls']:
        function_name = tool_call['function']['name']
        function_args = tool_call['function']['arguments']
        
        result = await self.mcp_client.call_tool(
            function_name,
            function_args
        )
        
        # Standard tool response format
        self.messages.append({
            "role": "tool",
            "content": result
        })
    
    # Continue conversation naturally
    response = self.client.chat(
        model=self.model,
        messages=self.messages,
        tools=self.tools
    )
```

**Winner: Ollama** ✅ - Cleaner loop, standard message format, no workarounds

---

## Feature Comparison

| Feature | Gemini | Ollama |
|---------|--------|--------|
| **API Key Required** | ✅ Yes | ❌ No |
| **Privacy** | Cloud-based | ✅ Local |
| **Cost** | Pay per token | ✅ Free |
| **Speed** | Network latency | ✅ Local inference |
| **Model Choice** | Gemini only | ✅ Many models |
| **Code Complexity** | Complex types | ✅ Simple dicts |
| **Setup** | API key setup | ✅ Just install |

## Performance Notes

### Ollama Advantages
1. **No API Key Management** - Just install and run
2. **Privacy** - Data never leaves your machine
3. **Cost** - Completely free
4. **Flexibility** - Easy to switch models
5. **Simpler Code** - Standard Python dictionaries, no special types

### Gemini Advantages
1. **No Local Resources** - Runs in the cloud
2. **Latest Models** - Access to Google's newest models
3. **Scalability** - No hardware limitations

## Example Usage

### Running with Ollama

```bash
# 1. Start Ollama (one time)
ollama serve

# 2. Pull a model (one time)
ollama pull llama3.1:latest

# 3. Start Barry server
cd barry-mcp-server
uv run barry-server

# 4. Run Ollama client
cd barry-client
uv run python -m barry_client.ollama_agent
```

### Running with Gemini

```bash
# 1. Get API key from Google AI Studio
# 2. Add to .env file

# 3. Start Barry server
cd barry-mcp-server
uv run barry-server

# 4. Run Gemini client
cd barry-client
uv run python -m barry_client.gemini_agent
```

## Recommended Models for Ollama

Based on function calling capability:

1. **qwen2.5-coder:7b** ⭐ - Best for coding tasks, excellent function calling
2. **llama3.1:8b** - Good general purpose, reliable function calling
3. **mistral:7b** - Fast and capable
4. **deepseek-coder:6.7b** - Specialized for code

## Conclusion

**For most use cases, Ollama is the better choice:**
- ✅ Simpler code (12% less)
- ✅ No API key needed
- ✅ Free and private
- ✅ Easy to switch models
- ✅ Standard Python patterns

**Use Gemini when:**
- You need cloud-based inference
- You want the latest Google models
- You don't want to manage local resources

## Code Statistics

```
Lines of Code:
- ollama_agent.py: ~180 lines
- gemini_agent.py: ~204 lines

Reduction: 12% less code with Ollama
Complexity: Significantly simpler API
```
