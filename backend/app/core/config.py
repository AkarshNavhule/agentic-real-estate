from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic Real Estate API"
    VERSION: str = "1.0.0"

    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_SEARCH_ENDPOINT: str = ""
    AZURE_SEARCH_KEY: str = ""

    # Add the 3 new variables here
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""
    AZURE_SEARCH_INDEX_NAME: str = ""
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = ""

    AZURE_OPENAI_CHAT_ENDPOINT: str = ""
    AZURE_OPENAI_CHAT_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"  # Tells Pydantic to ignore extra variables in the .env file


settings = Settings()