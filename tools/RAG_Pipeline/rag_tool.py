import os

from dotenv import load_dotenv
from google import genai

from tools.RAG_Pipeline.retrieval_tool import retrieve_documents


load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def build_context(
    documents: list
) -> str:

    context_parts = []

    for index, document in enumerate(
        documents
    ):

        context_parts.append(
            f"""
--- Relevant Document {index + 1} ---

{document['text']}
"""
        )

    return "\n".join(
        context_parts
    )


def answer_question(
    source_id: str,
    question: str,
    top_k: int = 5
) -> dict:

    print()
    print("=" * 60)
    print("RAG RETRIEVAL")
    print("=" * 60)

    documents = retrieve_documents(
        source_id=source_id,
        question=question,
        top_k=top_k
    )

    if not documents:

        return {
            "question": question,
            "answer": (
                "I could not find relevant "
                "information in the video."
            ),
            "documents": []
        }

    context = build_context(
        documents
    )

    prompt = f"""
You are a question-answering assistant
for a video knowledge system.

Answer the user's question ONLY using
the provided video context.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not invent information.
3. If the answer is not present in the
   context, clearly say that the video
   does not provide enough information.
4. Give a direct and useful answer.
5. Preserve the meaning of the speaker.
6. If the question asks for multiple
   points, organize them clearly.

VIDEO CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    print()
    print(
        f"Retrieved documents: "
        f"{len(documents)}"
    )

    print(
        f"Calling Gemini: {GEMINI_MODEL}"
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    answer = (
        response.text
        if response.text
        else "No answer generated."
    )

    return {
        "question": question,
        "answer": answer,
        "documents": documents
    }