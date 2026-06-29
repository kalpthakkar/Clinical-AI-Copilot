class OntologyMapper:

    def map_answer(self, question_id, text):

        text_lower = text.lower()

        if any(x in text_lower for x in ["no", "never", "none"]):
            return "NO", 0.95

        if any(x in text_lower for x in ["yes", "had", "did"]):
            return "YES", 0.9

        return "UNKNOWN", 0.6