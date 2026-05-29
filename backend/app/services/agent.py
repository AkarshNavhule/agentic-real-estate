from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions import KernelArguments

from app.mcp.tools import PropertyManagementPlugin
from app.services.search import retrieve_property_context
from app.core.config import settings

async def ask_real_estate_agent(user_query: str) -> str:
    # 1. Initialize the Kernel
    kernel = Kernel()

    # 2. Add the Azure OpenAI Chat Service
    chat_service = AzureChatCompletion(
        deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        endpoint=settings.AZURE_OPENAI_CHAT_ENDPOINT,
        api_key=settings.AZURE_OPENAI_CHAT_KEY,
        api_version="2024-02-01"
    )
    kernel.add_service(chat_service)

    kernel.add_plugin(PropertyManagementPlugin(), plugin_name="CRM")

    # 3. Fetch relevant data from your Azure Search database
    property_context = await retrieve_property_context(user_query)

    # 4. Execution settings — note the correct parameter name
    execution_settings = AzureChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()  # ✅ Fixed
    )

    # 5. Create the System Prompt
    prompt_template = """
    You are an elite AI Real Estate Assistant. 
    Use ONLY the following property information to answer the user's question. 
    If the answer is not in the information below, say "I don't have information on that."

    PROPERTY INFORMATION:
    {{$context}}

    USER QUESTION: 
    {{$query}}
    """

    # 6. Execute the prompt
    arguments = KernelArguments(
        settings=execution_settings,
        context=property_context,
        query=user_query
    )
    response = await kernel.invoke_prompt(prompt_template, arguments=arguments)

    return str(response)