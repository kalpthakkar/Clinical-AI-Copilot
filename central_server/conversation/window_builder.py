from central_server.utils.token_counter import estimate_tokens


class WindowBuilder:

    def __init__(self, max_tokens=200):
        self.max_tokens = max_tokens

    def build_window(self, events):

        selected = []
        total_tokens = 0

        # traverse from latest backwards
        for event in reversed(events):

            text = f"{event['speaker']}: {event['text']}"
            tokens = estimate_tokens(text)

            if total_tokens + tokens > self.max_tokens:
                break

            selected.append(text)
            total_tokens += tokens

        return "\n".join(reversed(selected)), total_tokens