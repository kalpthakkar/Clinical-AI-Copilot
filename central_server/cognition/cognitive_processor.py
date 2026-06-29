import time
from pprint import pprint
from central_server.conversation.buffer import ConversationBuffer
from central_server.conversation.window_builder import WindowBuilder
from central_server.llm.async_extractor import AsyncExtractor
from central_server.cognition.entity_processor import EntityProcessor

class CognitiveProcessor:

    def __init__(self):

        self.buffer = ConversationBuffer()
        self.min_tokens_to_call_llm = 150
        self.max_tokens_per_asr_event = 500
        self.window_builder = WindowBuilder(max_tokens=self.max_tokens_per_asr_event)
        self.extractor = AsyncExtractor(model='llama3.1:latest')
        self.entity_processor = EntityProcessor()

        self.last_trigger_time = 0
        self.cooldown_seconds = 3

    # -----------------------------
    # Add new ASR event
    # -----------------------------
    def on_new_event(self, event):

        event_dict = {
            "speaker": event.speaker,
            "text": event.transcript,
            "timestamp": str(event.timestamp_start.isoformat())
        }

        self.buffer.add_event(event_dict)

        self._maybe_trigger_extraction()

    # -----------------------------
    # Trigger logic
    # -----------------------------
    def _maybe_trigger_extraction(self):

        now = time.time()

        if now - self.last_trigger_time < self.cooldown_seconds:
            return

        unprocessed = self.buffer.get_unprocessed_events()

        if not unprocessed:
            return

        context_text, tokens = self.window_builder.build_window(unprocessed)

        if tokens < self.min_tokens_to_call_llm:
            return

        print(f"\n🤖 Triggering LLM extraction (tokens={tokens})...\n")

        self.last_trigger_time = now

        self.extractor.submit(context_text, self._handle_result)

        self.buffer.mark_processed()

    # -----------------------------
    # Callback from async worker
    # -----------------------------
    def _handle_result(self, result):

        print("\n🧠 LLM Response:\n", result, "\n")

        entities = result.get("entities", [])

        processed_entities = self.entity_processor.process(entities)

        print("\n✅ Processed Entities:\n", processed_entities, "\n")

        print("\n📦 Entity Store:\n", self.entity_processor.store.get_all(), "\n")

        # TODO: integrate into clinical state