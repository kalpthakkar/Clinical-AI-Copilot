from typing import List


class ConversationBuffer:

    def __init__(self):
        self.events: List[dict] = []
        self.last_processed_index = 0

    def add_event(self, event_dict):
        self.events.append(event_dict)

    def get_unprocessed_events(self):
        return self.events[self.last_processed_index:]

    def mark_processed(self):
        self.last_processed_index = len(self.events)

    def get_all_events(self):
        return self.events