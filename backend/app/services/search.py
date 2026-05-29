from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from app.core.config import settings

# Initialize the OpenAI client for creating embeddings
openai_client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2023-05-15",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

# Initialize the Azure AI Search client
search_client = SearchClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    index_name=settings.AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
)

async def retrieve_property_context(query: str) -> str:
    """Embeds the user's query and searches the vector database."""
    try:
        # 1. Turn the user's question into a vector (numbers)
        embedding_response = openai_client.embeddings.create(
            input=query,
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME # Use settings here!
        )
        query_vector = embedding_response.data[0].embedding

        # 2. Search the Azure database
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=3,
            fields="embedding"
        )

        results = search_client.search(
            search_text=query,  # Hybrid search (keyword + vector)
            vector_queries=[vector_query],
            top=3
        )

        # 3. Format the results into a single text block for the LLM
        context = ""
        for result in results:
            context += f"- {result['title']} ({result['price']}): {result['description']}\n"

        return context if context else "No relevant properties found in the database."

    except Exception as e:
        print(f"Search error: {e}")
        return "Error retrieving property data."