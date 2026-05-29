import os
from typing import AsyncGenerator
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import \
    AzureChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments
from app.services.search import retrieve_property_context
from app.core.config import settings
from app.mcp.tools import PropertyManagementPlugin

# GLOBAL MEMORY STORE
conversation_memory = {}


def _setup_kernel_and_arguments(user_query: str, session_id: str, property_context: str):
    """Helper function to avoid repeating the setup code for both streaming and non-streaming."""
    kernel = Kernel()

    chat_service = AzureChatCompletion(
        deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        endpoint=settings.AZURE_OPENAI_CHAT_ENDPOINT,
        api_key=settings.AZURE_OPENAI_CHAT_KEY,
        api_version="2024-02-01"
    )
    kernel.add_service(chat_service)
    kernel.add_plugin(PropertyManagementPlugin(), plugin_name="CRM")

    execution_settings = AzureChatPromptExecutionSettings(
        service_id="default",
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    history_text = "\n".join(conversation_memory[session_id])

    prompt_template = """
    You are an elite AI Real Estate Assistant. 
    Use ONLY the following property information to answer the user's question. 
    If the answer is not in the information below, say "I don't have information on that."
    If the user asks about tours, use your CRM plugin tool to find the schedule.

    PAST CONVERSATION HISTORY:
    {{$history}}

    PROPERTY INFORMATION:
    {{$context}}

    USER QUESTION: 
    {{$query}}
    """

    arguments = KernelArguments(
        settings=execution_settings,
        context=property_context,
        history=history_text,
        query=user_query
    )

    return kernel, prompt_template, arguments


# ==========================================
# API 1: STANDARD BLOCKING CALL (NON-STREAM)
# ==========================================
async def ask_real_estate_agent(user_query: str, session_id: str) -> str:
    property_context = await retrieve_property_context(user_query)
    kernel, prompt_template, arguments = _setup_kernel_and_arguments(user_query, session_id, property_context)

    response = await kernel.invoke_prompt(prompt_template, arguments=arguments)

    # Save to memory
    conversation_memory[session_id].append(f"User: {user_query}")
    conversation_memory[session_id].append(f"Assistant: {str(response)}")
    conversation_memory[session_id] = conversation_memory[session_id][-6:]

    return str(response)


# ==========================================
# API 2: STREAMING CALL (TOKEN-BY-TOKEN)
# ==========================================
async def ask_real_estate_agent_stream(user_query: str, session_id: str) -> AsyncGenerator[str, None]:
    property_context = await retrieve_property_context(user_query)
    kernel, prompt_template, arguments = _setup_kernel_and_arguments(user_query, session_id, property_context)

    full_response = ""

    async for chunk in kernel.invoke_prompt_stream(prompt_template, arguments=arguments):
        token = str(chunk[0])
        if token:
            full_response += token
            yield token

            # Save to memory after the stream completes
    conversation_memory[session_id].append(f"User: {user_query}")
    conversation_memory[session_id].append(f"Assistant: {full_response}")
    conversation_memory[session_id] = conversation_memory[session_id][-6:]