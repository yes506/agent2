import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from agents.wikipedia_tool import get_wiki_single_page, get_wiki_summary

load_dotenv()


def generate_embeddings(source_text: str):
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_EMBEDDING_MODEL_API_KEY"),
        api_version=os.getenv("AZURE_EMBEDDING_MODEL_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_EMBEDDING_MODEL_ENDPOINT"),
    )
    model = os.getenv("AZURE_EMBEDDING_MODEL_DEPLOYMENT_NAME")

    embedding_values = client.embeddings.create(input=[source_text], model=model).data[0].embedding

    return embedding_values


if __name__ == "__main__":
    source_text = get_wiki_summary("경복궁")
    source_text = source_text.replace("\n", " ")
    generate_embeddings(source_text)
