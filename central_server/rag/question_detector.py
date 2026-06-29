# central_server/nlp/matcher.py

import json
import math
from typing import Dict, List, Literal, Optional
from pathlib import Path
import ollama
from central_server.config.env_config import EMBEDDING_MODEL_NAME, EMBEDDINGS_PATH

class QuestionDetector():

    def __init__(self):
        
        # ---------------- LOAD EMBEDDINGS ----------------

        with open(EMBEDDINGS_PATH, "r") as f:
            self.EMBEDDINGS_DATA = json.load(f)

    # ---------------- UTILS ----------------

    def _normalize_text(self, text: str) -> str:
        return (
            str(text)
            .lower()
            .replace("*", "")
            .replace(":", "")
            .replace("?", "")
            .strip()
        )


    def _cosine_normalized(self, a, b):
        """Dot product for normalized vectors"""
        return sum(x * y for x, y in zip(a, b))


    def _cosine_general(self, a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb)


    def _get_embedding(self, text: str):
        response = ollama.embed(
            model=EMBEDDING_MODEL_NAME,
            input=text
        )
        return response["embeddings"][0]


    # ---------------- CORE MATCH FUNCTION ----------------

    def detect(
        self,
        input_text: str,
        use_normalized=True,
        full_scan=False,
        debug=False,
    ) -> Optional[Dict[Literal['question_id', 'question', 'match_score'], str | float]]:
        """
        Returns:
            {
                "question_id": "DAY_LOOKOUT",
                "question": "How are you feeling today?",
                "match_score": 0.91
            }
            OR None if no match
        """

        normalized = self._normalize_text(input_text)

        # 1️⃣ Embed input
        input_vector = self._get_embedding(normalized)

        similarity_fn = self._cosine_normalized if use_normalized else self._cosine_general

        best_match = None
        best_score = -1

        # 2️⃣ Iterate all stored labels
        for question_key, group in self.EMBEDDINGS_DATA["questions"].items():
            for label in group["labels"]:
                label_vector = label["embedding"]
                threshold = label["threshold"]

                score = similarity_fn(input_vector, label_vector)

                if debug:
                    print(f"[DEBUG] {question_key} :: {label['text']} → {score:.3f} (th={threshold})")

                # 3️⃣ Check threshold
                if score >= threshold and score > best_score:
                    best_score = score
                    best_match = {
                        "question_id": question_key,
                        "question": label["text"],
                        "match_score": round(score, 3),
                    }
                    break
            
            if best_match and not full_scan:
                break

        return best_match