from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str ="Agentic Real Estate API"
    VERSION: str ="1.0.0"

    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_SEARCH_ENDPOINT: str = ""
    AZURE_SEARCH_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()



