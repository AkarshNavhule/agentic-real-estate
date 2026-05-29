from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions import KernelArguments
from typing import AsyncGenerator
from app.mcp.tools import PropertyManagementPlugin
from app.services.search import retrieve_property_context
from app.core.config import settings

# Shared in-memory conversation store
conversation_memory: dict[str, list[str]] = {}

PROMPT_TEMPLATE = """
You are an elite AI Real Estate Assistant. 
Use ONLY the following property information to answer the user's question. 
If the answer is not in the information below, say "I don't have information on that."

CONVERSATION HISTORY:
{{$history}}

PROPERTY INFORMATION:
{{$context}}

USER QUESTION: 
{{$query}}
"""

def _build_kernel() -> Kernel:
    """Shared kernel factory reused by both agent functions."""
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(
        deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        endpoint=settings.AZURE_OPENAI_CHAT_ENDPOINT,
        api_key=settings.AZURE_OPENAI_CHAT_KEY,
        api_version="2024-02-01"
    ))
    kernel.add_plugin(PropertyManagementPlugin(), plugin_name="CRM")
    return kernel

def _get_history(session_id: str) -> str:
    """Returns formatted conversation history for a session."""
    return "\n".join(conversation_memory.get(session_id, []))

def _save_to_memory(session_id: str, user_query: str, response: str):
    """Appends the latest turn to memory and trims to last 6 messages."""
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    conversation_memory[session_id].append(f"User: {user_query}")
    conversation_memory[session_id].append(f"Assistant: {response}")
    # Keep only last 6 messages to avoid token overflow
    conversation_memory[session_id] = conversation_memory[session_id][-6:]


async def ask_real_estate_agent(user_query: str, session_id: str) -> str:
    kernel = _build_kernel()
    property_context = await retrieve_property_context(user_query)

    execution_settings = AzureChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )
    arguments = KernelArguments(
        settings=execution_settings,
        context=property_context,
        history=_get_history(session_id),
        query=user_query
    )

    response = await kernel.invoke_prompt(PROMPT_TEMPLATE, arguments=arguments)
    response_text = str(response)

    _save_to_memory(session_id, user_query, response_text)

    return response_text


async def ask_real_estate_agent_stream(
    user_query: str,
    session_id: str
) -> AsyncGenerator[str, None]:
    kernel = _build_kernel()
    property_context = await retrieve_property_context(user_query)

    execution_settings = AzureChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )
    arguments = KernelArguments(
        settings=execution_settings,
        context=property_context,
        history=_get_history(session_id),
        query=user_query
    )

    full_response = ""

    async for chunk in kernel.invoke_prompt_stream(PROMPT_TEMPLATE, arguments=arguments):
        token = str(chunk[0])
        if token:
            full_response += token
            yield f"data: {token}\n\n"   # SSE format

    # Signal end of stream to the client
    yield "data: [DONE]\n\n"

    _save_to_memory(session_id, user_query, full_response)