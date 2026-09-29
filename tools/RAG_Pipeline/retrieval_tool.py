from tools.RAG_Pipeline.embedding_tool import create_embeddings
from tools.RAG_Pipeline.vector_store_tool import get_chroma_collection


TOP_K = 5


def retrieve_documents(
    source_id: str,
    question: str,
    top_k: int = TOP_K
) -> list:

    if not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )

    collection = get_chroma_collection(
        source_id
    )

    query_embedding = create_embeddings(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    retrieved = []

    for index, document in enumerate(
        documents
    ):

        retrieved.append(
            {
                "text": document,
                "metadata": (
                    metadatas[index]
                    if index < len(metadatas)
                    else {}
                ),
                "distance": (
                    distances[index]
                    if index < len(distances)
                    else None
                )
            }
        )

    return retrieved