import os

import chromadb

from tools.RAG_Pipeline.embedding_tool import create_embeddings


def get_chroma_collection(
    source_id: str
):

    persist_directory = os.path.join(
        "storage",
        "chroma"
    )

    os.makedirs(
        persist_directory,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=persist_directory
    )

    collection_name = (
        f"source_{source_id}"
    )

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": "cosine"
        }
    )

    return collection


def store_chunks(
    source_id: str,
    chunks: list
):

    if not chunks:

        raise ValueError(
            "No chunks to store."
        )

    collection = get_chroma_collection(
        source_id
    )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = create_embeddings(
        texts
    )

    ids = [
        f"chunk_{chunk['chunk_id']}"
        for chunk in chunks
    ]

    metadatas = []

    for chunk in chunks:

        metadatas.append(
            {
                "source_id": source_id,
                "chunk_id": chunk["chunk_id"],
                "start_char": chunk["start_char"],
                "end_char": chunk["end_char"]
            }
        )

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print()
    print("=" * 60)
    print("CHROMADB")
    print("=" * 60)

    print(
        f"Stored {len(chunks)} chunks."
    )

    print(
        f"Collection: {collection.name}"
    )

    return collection