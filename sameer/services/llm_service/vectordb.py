import pandas as pd

from Sameer.config import settings

from qdrant_client import QdrantClient, models
from qdrant_client.conversions import common_types as types

from llama_index.embeddings.openai import OpenAIEmbedding


def get_qdrant_client() -> QdrantClient | None:
    client = None
    try:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
    except Exception as e:
        print(f"Error while connecting to qdrant: {e}")
    return client


def get_qdrant_collections() -> types.CollectionsResponse:
    collections = []
    try:
        client = get_qdrant_client()
        if client:
            collections = client.get_collections()
    except Exception as e:
        print(f"Error while getting collections: {e}")
    return collections


def get_openai_embeddings(
    embedding_model: str = "text-embedding-3-small",
) -> OpenAIEmbedding:
    embed_model = OpenAIEmbedding(
        model=embedding_model, api_key=settings.OPENAI_API_KEY
    )
    return embed_model


def get_text_embeddings(query: str) -> list[float]:
    embedding_model = get_openai_embeddings()
    embedded_vector = embedding_model.get_text_embedding(query)
    return embedded_vector


def upload_vectors_to_qdrant(
    dataframe: pd.DataFrame,
    vector: list[float],
    collection_name: str = "movies_metadata",
) -> None:
    client = get_qdrant_client()  # TODO: Make it use dependancy injection

    if not isinstance(embedded_vector, list[float]):
        embedded_vector = get_text_embeddings(vector)

    try:
        print("Uploading points...")
        client.upload_points(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=df["id"],
                    vector=embedded_vector[idx],
                )
                for idx, df in dataframe.iterrows()
            ],
        )
        print("Uploading points was successful!")
    except Exception as e:
        print(f"Something went wrong: {e}")


def search_vectordb(
    query_vector: list[float],
    returned_vectors: int = 5,
    collection_name: str = "movies_metadata",
) -> list[types.ScoredPoint]:
    client = get_qdrant_client()  # TODO: Make it use dependancy injection
    response = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=returned_vectors,
    )
    return response


#! TESTING PURPOSES
if __name__ == "__main__":
    print("-------- Get Qdrant Client --------")
    print(get_qdrant_client())
    print("-------- Get Qdrant Collections --------")
    print(get_qdrant_collections())
    print("-------- Testing OpenAI Embeddings --------")
    print(f"Mamdouh is the same is {get_text_embeddings('Mamdouh')}")
