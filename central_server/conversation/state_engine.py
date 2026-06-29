from collections import deque
from datetime import datetime


class ConversationStateEngine:

    def __init__(self, max_history=10):

        # recent utterances (for context)
        self.history = deque(maxlen=max_history)

        # active questions awaiting answers
        self.active_questions = {}

        # resolved Q/A pairs
        self.resolved = []

    # ----------------------------------
    # Add new event to conversation
    # ----------------------------------
    def add_event(self, event):

        self.history.append({
            "speaker": event.speaker,
            "text": event.transcript,
            "timestamp": event.timestamp_start.isoformat()
        })

    # ----------------------------------
    # Register doctor questions
    # ----------------------------------
    def register_question(self, question_id, event):
        self.active_questions[question_id] = {
                "question_text": event.transcript,
                "timestamp": event.timestamp_start.isoformat(),
                "speaker": event.speaker
            }

    # ----------------------------------
    # Resolve patient answers
    # ----------------------------------
    def resolve_answers(self, event):

        if event.speaker != "patient":
            return []

        resolved_pairs = []

        for q_id, q_data in list(self.active_questions.items()):

            resolved_pairs.append({
                "question_id": q_id,
                "question": q_data["question_text"],
                "answer": event.transcript,
                "question_time": q_data["timestamp"],
                "answer_time": event.timestamp_start.isoformat()
            })

        # Clear after resolution (simple strategy)
        self.active_questions.clear()

        self.resolved.extend(resolved_pairs)

        return resolved_pairs

    # ----------------------------------
    # Get conversation context
    # ----------------------------------
    def get_context(self):

        return list(self.history)

    # ----------------------------------
    # Debug view
    # ----------------------------------
    def debug_state(self):

        return {
            "active_questions": self.active_questions,
            "history": list(self.history),
            "resolved": self.resolved[-5:]
        }