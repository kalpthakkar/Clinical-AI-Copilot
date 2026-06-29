# central_server/nlp/generate_embeddings.py

import json
import re
from datetime import timezone, datetime
import ollama
import os
from central_server.config.env_config import EMBEDDING_MODEL_NAME, EMBEDDINGS_PATH

from central_server.rag.schema_registry import SCHEMAS

OUTPUT_VERSION = 1
NORMALIZE = True

# ===========================================================
# 🔹 NORMALIZE LABEL TEXT (match your JS logic)
# ===========================================================
def normalize_label(text: str) -> str:
    return (
        str(text)
        .lower()
        .replace("*", "")
        .replace(":", "")
        .replace("?", "")
        .strip()
    )


# ===========================================================
# 🔹 GET EMBEDDING FROM OLLAMA
# ===========================================================
def get_embedding(text: str):
    response = ollama.embed(
        model=EMBEDDING_MODEL_NAME,
        input=text
    )
    return response["embeddings"][0]


# ===========================================================
# 🔹 MAIN GENERATION
# ===========================================================
def run():
    output = {
        "version": OUTPUT_VERSION,
        "model": EMBEDDING_MODEL_NAME,
        "embeddingType": "semantic",
        "normalized": NORMALIZE,
        "dimensions": None,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "questions": {},
    }

    for question_key, schema in SCHEMAS.items():
        print(f"\n📌 Processing: {question_key}")

        labels_out = []

        for label_text, threshold_percent in schema["labels"]:
            normalized_text = normalize_label(label_text)

            print(f"  🔸 Embedding: \"{normalized_text}\"")

            vector = get_embedding(normalized_text)

            if output["dimensions"] is None:
                output["dimensions"] = len(vector)

            labels_out.append({
                "text": label_text,
                "normalizedText": normalized_text,
                "threshold": threshold_percent / 100,
                "embedding": vector,
            })

        output["questions"][question_key] = {
            "labels": labels_out,
            # "options": schema.get("options", [])
        }

    # ===========================================================
    # 💾 WRITE OUTPUT
    # ===========================================================
    with open(EMBEDDINGS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print("\n✅ Embeddings written to label_embeddings.json")


# ===========================================================
# 🚀 RUN
# ===========================================================
if __name__ == "__main__":
    run()