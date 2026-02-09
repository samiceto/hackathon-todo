"""
Agent Configuration - Run-Level Configuration Pattern.

This module defines the OpenAI Agents SDK run configuration, including
model settings, API clients, and tracing configuration.

Step 3: AI-Powered Chatbot - Agent Configuration
"""

import os
from dotenv import load_dotenv
from agents import OpenAIChatCompletionsModel, AsyncOpenAI
from agents.run import RunConfig

# Load environment variables
load_dotenv()

# Load OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY environment variable not set. "
        "Please add it to your .env file or environment."
    )

# Create async OpenAI client
client = AsyncOpenAI(api_key=api_key)

# Configure model (default: gpt-4)
model_name = os.getenv("OPENAI_MODEL", "gpt-4")

# Create OpenAI model instance
model = OpenAIChatCompletionsModel(
    model=model_name,
    openai_client=client
)

# Create run configuration
config = RunConfig(
    model=model,
    model_provider=client,
    # Enable tracing for debugging (set TRACING_DISABLED=true in .env to disable)
    tracing_disabled=os.getenv("TRACING_DISABLED", "false").lower() == "true"
)

# Export configuration
__all__ = ["config", "model", "client"]
