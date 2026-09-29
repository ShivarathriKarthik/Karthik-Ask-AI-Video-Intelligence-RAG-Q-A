from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


_model = None


def get_embedding_model():

    global _model

    if _model is None:

        print()
        print("Loading embedding model...")
        print(EMBEDDING_MODEL_NAME)

        _model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

    return _model


def create_embeddings(
    texts: list[str]
) -> list[list[float]]:

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()