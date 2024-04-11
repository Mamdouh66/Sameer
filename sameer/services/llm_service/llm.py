import requests

from Sameer.services.llm_service import vectordb
from Sameer.config import settings

from qdrant_client.conversions import common_types as types

from fastapi import HTTPException, status


class MoviesLLM:
    def __init__(self) -> None:
        self.client = vectordb.get_qdrant_client()

    def __get_omdp_data(imdb_id: str, omdp_api_key: str = settings.OMDP_API_KEY):
        url = f"http://www.omdbapi.com/?apikey={omdp_api_key}&i={imdb_id}"
        response = requests.get(url)
        data = response.json()
        if data["Response"] == "False":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with {imdb_id} returned with {data['Error']}",
            )
        return data

    def _search(query: str, limit: int = 5) -> list[types.ScoredPoint]:
        embedded_query = vectordb.get_text_embeddings(query=query)
        response = vectordb.search_vectordb(
            query_vector=embedded_query, returned_vectors=limit
        )
        return response

    def __get_imdb_id(movie_id: str): ...

    def get_movies(): ...
