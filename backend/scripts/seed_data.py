import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

# Load environment variables
load_dotenv()

# 1. Initialize Clients
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

search_index_client = SearchIndexClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# 2. Dummy Real Estate Data
properties = [
    {
        "id": "1",
        "title": "Luxury Villa in Koramangala",
        "price": "$500,000",
        "description": "A beautiful 4-bedroom villa in the heart of Bangalore. Features a private pool, modern kitchen, and smart home automation. Perfect for tech executives."
    },
    {
        "id": "2",
        "title": "Cozy Apartment in Indiranagar",
        "price": "$150,000",
        "description": "2-bedroom apartment with a vibrant neighborhood view. Walking distance to the best cafes and metro station. Ideal for young professionals."
    },
    {
        "id": "3",
        "title": "Malnad Estate Commercial Office",
        "price": "$1,200,000",
        "description": "Prime commercial real estate spanning 5000 sqft. Pre-wired for enterprise networking. Includes 10 dedicated parking spots."
    }
]


def create_index():
    print(f"Creating index: {INDEX_NAME}...")

    # Define the fields (Columns) in our Vector Database
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="price", type=SearchFieldDataType.String),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile")
    ]

    # Configure Vector Search Algorithm
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
    )

    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    search_index_client.create_or_update_index(index)
    print("Index created successfully!")


def generate_embeddings_and_upload():
    print("Generating embeddings and uploading documents...")
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
    )

    docs_to_upload = []
    for prop in properties:
        # Create a single string of text to embed
        text_to_embed = f"Title: {prop['title']} \nPrice: {prop['price']} \nDescription: {prop['description']}"

        # Call Azure OpenAI to convert text to a 1536-dimension number array
        response = openai_client.embeddings.create(
            input=text_to_embed,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        )

        # Add the embedding to our document
        prop["embedding"] = response.data[0].embedding
        docs_to_upload.append(prop)

    # Upload to Azure Search
    search_client.upload_documents(documents=docs_to_upload)
    print("Documents uploaded successfully!")


if __name__ == "__main__":
    create_index()
    generate_embeddings_and_upload()