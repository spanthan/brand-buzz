from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://brandbuzz_user:brandbuzz_pass@localhost:5432/brandbuzz"

    class Config:
        env_file = ".env"

settings = Settings()