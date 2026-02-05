"""Elasticsearch retriever tool."""

from langchain_core.tools import tool
from langchain_elasticsearch import ElasticsearchStore
from langchain_ollama import OllamaEmbeddings
from elasticsearch import Elasticsearch

from src.config.config import Config


def get_elasticsearch_client():
    """Create Elasticsearch client with authentication."""
    auth_params = {}

    if Config.ELASTICSEARCH_API_KEY:
        auth_params["api_key"] = Config.ELASTICSEARCH_API_KEY
    elif Config.ELASTICSEARCH_USER and Config.ELASTICSEARCH_PASSWORD:
        auth_params["basic_auth"] = (
            Config.ELASTICSEARCH_USER,
            Config.ELASTICSEARCH_PASSWORD
        )

    return Elasticsearch(
        Config.ELASTICSEARCH_URL,
        **auth_params
    )


def get_retriever():
    """Get configured Elasticsearch vector retriever.

    Uses Ollama embeddings for semantic search.
    """
    # Initialize embeddings with dedicated embedding model
    embeddings = OllamaEmbeddings(
        model=Config.OLLAMA_EMBEDDING_MODEL,
        base_url=Config.OLLAMA_BASE_URL
    )

    # Create vector store
    vector_store = ElasticsearchStore(
        es_url=Config.ELASTICSEARCH_URL,
        index_name=Config.ELASTICSEARCH_INDEX,
        embedding=embeddings,
    )

    # Return as retriever with top 5 results
    return vector_store.as_retriever(search_kwargs={"k": 5})


@tool
def search_documents(query: str) -> str:
    """Search documents in Elasticsearch.

    Args:
        query: Search query string

    Returns:
        Retrieved documents as formatted string
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)

        if not docs:
            return "No documents found."

        result = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content[:200]  # Limit content length
            result.append(f"{i}. {content}")

        return "\n\n".join(result)

    except Exception as e:
        return f"Error searching documents: {str(e)}"
