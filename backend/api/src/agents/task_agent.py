"""
Task Management Agent using OpenAI Agents SDK with MCP Integration.

This agent provides conversational task management capabilities by integrating
with the MCP (Model Context Protocol) server that exposes task management tools.

Step 3: AI-Powered Chatbot - OpenAI Agents SDK Integration
"""


from agents import Agent
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings


# System prompt for the task management agent
TASK_AGENT_INSTRUCTIONS = """You are a helpful task management assistant that helps users organize their todos.

Your capabilities:
- Add tasks: Create new tasks with titles and optional descriptions
- List tasks: Show all tasks, completed tasks, or incomplete tasks
- Complete tasks: Mark tasks as done or undone
- Update tasks: Modify task titles or descriptions
- Delete tasks: Permanently remove tasks

Natural Language Understanding:
- When a user says "add a task...", "create a task...", or "remember to...", use todo_add_task
- When a user asks "show my tasks", "what do I need to do", or "list tasks", use todo_list_tasks
- When a user says "mark task X as complete", "I finished task X", or "complete task X", use todo_complete_task
- When a user says "change task X to...", "update task X...", or "rename task X", use todo_update_task
- When a user says "delete task X", "remove task X", or "get rid of task X", use todo_delete_task

Response Guidelines:
- Always confirm actions with clear, friendly messages
- When listing tasks, use the markdown format for better readability
- For ambiguous requests, ask clarifying questions
- Extract task details from natural language (e.g., "Buy milk tomorrow" → title: "Buy milk", description: "tomorrow")
- Use the user_id parameter from the conversation context for all operations

Conversation Style:
- Be conversational and friendly
- Acknowledge completed actions clearly
- Provide helpful suggestions when appropriate
- If a user's request is unclear, ask for clarification rather than guessing

Error Handling:
- If a task is not found, suggest listing tasks to see available options
- If an operation fails, explain why in simple terms and suggest next steps
- Always maintain a helpful tone, even when errors occur
"""


def create_task_agent(mcp_server_url: str, agent_name: str = "Task Assistant") -> Agent:
    """Create a task management agent with MCP tool integration.

    This factory function creates an agent configured to use the MCP server
    tools for task management. The agent understands natural language and
    maps user requests to appropriate tool calls.

    Args:
        mcp_server_url (str): URL of the MCP server (e.g., "http://localhost:8000/mcp")
        agent_name (str): Display name for the agent (default: "Task Assistant")

    Returns:
        Agent: Configured task management agent with MCP tools

    Example:
        agent = create_task_agent(mcp_server_url="http://localhost:8000/mcp")
        # Agent is ready to handle conversational task management
    """
    # Note: MCP server connection is managed by the caller context
    # This function returns the agent configuration
    agent = Agent(
        name=agent_name,
        instructions=TASK_AGENT_INSTRUCTIONS,
        model_settings=ModelSettings(
            # Allow agent to decide when to use tools based on conversation
            tool_choice="auto",
            # Enable parallel tool calls for efficiency
            parallel_tool_calls=True,
            # Temperature for more natural conversations
            temperature=0.7,
        ),
    )

    return agent


async def create_agent_with_mcp(
    mcp_server_url: str,
    agent_name: str = "Task Assistant"
) -> tuple[Agent, MCPServerStreamableHttp]:
    """Create task agent and MCP server connection.

    This is a convenience function that creates both the agent and establishes
    the MCP server connection. Use this in async contexts where you need both.

    Args:
        mcp_server_url (str): URL of the MCP server
        agent_name (str): Display name for the agent

    Returns:
        tuple[Agent, MCPServerStreamableHttp]: Agent instance and MCP server connection

    Example:
        async with create_agent_with_mcp("http://localhost:8000/mcp") as (agent, mcp_server):
            # Use agent with MCP tools
            result = await Runner.run(agent, "Add a task to buy groceries", config=config)
    """
    # Create MCP server connection
    mcp_server = MCPServerStreamableHttp(
        name="Todo MCP Server",
        params={"url": mcp_server_url},
    )

    # Create agent with MCP server
    agent = Agent(
        name=agent_name,
        instructions=TASK_AGENT_INSTRUCTIONS,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(
            tool_choice="auto",
            parallel_tool_calls=True,
            temperature=0.7,
        ),
    )

    return agent, mcp_server


# Pre-configured agent variations for different use cases

def create_strict_agent(mcp_server_url: str) -> Agent:
    """Create a task agent that always uses tools for all requests.

    This variant is more deterministic and forces tool use for every interaction,
    useful for testing or when you want predictable behavior.

    Args:
        mcp_server_url (str): URL of the MCP server

    Returns:
        Agent: Task agent with strict tool usage
    """
    agent = Agent(
        name="Strict Task Assistant",
        instructions=TASK_AGENT_INSTRUCTIONS + "\n\nIMPORTANT: Always use tools to answer questions. Never respond without using at least one tool.",
        model_settings=ModelSettings(
            tool_choice="required",  # Force tool usage
            parallel_tool_calls=True,
            temperature=0.3,  # Lower temperature for more predictable responses
        ),
    )

    return agent


def create_conversational_agent(mcp_server_url: str) -> Agent:
    """Create a task agent optimized for natural conversation.

    This variant prioritizes natural language responses and only uses tools
    when necessary, making it feel more like chatting with a person.

    Args:
        mcp_server_url (str): URL of the MCP server

    Returns:
        Agent: Task agent optimized for conversation
    """
    agent = Agent(
        name="Conversational Task Assistant",
        instructions=TASK_AGENT_INSTRUCTIONS + "\n\nPrioritize natural, friendly conversation. Use tools when needed to help the user, but feel free to chat and ask questions.",
        model_settings=ModelSettings(
            tool_choice="auto",
            parallel_tool_calls=False,  # Sequential for more natural flow
            temperature=0.9,  # Higher temperature for more varied responses
        ),
    )

    return agent


# Example usage patterns (for reference)
"""
# Basic usage with runner:
from agents import Runner
from agents.run import RunConfig
from config import config  # Your run-level config

agent, mcp_server = await create_agent_with_mcp("http://localhost:8000/mcp")

async with mcp_server:
    result = await Runner.run(
        starting_agent=agent,
        input="Add a task to buy groceries",
        config=config
    )
    print(result.final_output)

# Usage in FastAPI chat endpoint:
async def chat_endpoint(user_id: int, message: str):
    agent, mcp_server = await create_agent_with_mcp("http://localhost:8000/mcp")

    # Inject user_id into conversation context
    context = {"user_id": user_id}

    async with mcp_server:
        result = await Runner.run(
            starting_agent=agent,
            input=message,
            context=context,
            config=config
        )
        return result.final_output
"""
