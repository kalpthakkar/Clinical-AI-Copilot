import spacy
from typing import List

class SentenceSplitter:
    """
    High-performance sentence splitter using spaCy sentencizer.
    Designed for real-time applications.
    """

    def __init__(self):
        # Create lightweight pipeline (no model load)
        self.nlp = spacy.blank("en")
        self.nlp.add_pipe("sentencizer")

    def split(self, text: str) -> List[str]:
        if not text:
            return []

        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


# Singleton instance (important for real-time systems)
_splitter = SentenceSplitter()

def split_sentences(text: str) -> List[str]:
    return _splitter.split(text)


if __name__ == "__main__":
    sample_text = """
    Dr. Smith went to Washington, D.C. on Jan. 3rd.
    He arrived at 3.14 p.m. "This is amazing!" he said.
    But was it? Yes... it was.
    """

    sentences = split_sentences(sample_text)

    for i, s in enumerate(sentences, 1):
        print(f"{i}: {s}")