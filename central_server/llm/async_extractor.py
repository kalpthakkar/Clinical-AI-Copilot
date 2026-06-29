from concurrent.futures import ThreadPoolExecutor
from modules.ollama.services.interaction_service import InteractionService
from modules.ollama.chain.prompt_models import PromptStep
from modules.ollama.core.enums import PromptRole, ResponseFormat


class AsyncExtractor:

    def __init__(self, model="phi3:latest"):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.service = InteractionService(default_model=model)
        self.session_id = self.service.create_session()

    # -----------------------------
    # Submit async job
    # -----------------------------
    def submit(self, context_text, callback):

        self.executor.submit(self._run_extraction, context_text, callback)

    # -----------------------------
    # LLM execution
    # -----------------------------
    def _run_extraction(self, context_text, callback):

        prompt = f"""
You are a precise clinical extraction engine for dentistry.

Analyze the conversation below and extract structured insights.

Conversation:
{context_text}

Return STRICT JSON:

{{
  "entities": [
    {{
      "type": "procedure | symptom | condition | medication",
      "value": "",
      "tooth_location": "",
      "time": "",
      "speaker": ""
    }}
  ],
  "questions": [
    {{
      "text": "",
      "speaker": ""
    }}
  ]
}}

Rules:
- Only extract clinically relevant information
- If nothing relevant, return empty arrays
- Output MUST be valid JSON
"""

        chain = [
            PromptStep(
                role=PromptRole.USER,
                content=prompt,
                response_format=ResponseFormat.JSON,
                persist=False,
                persist_response=False,
                expect_response=True,
                json_schema={
                    "type": "object",
                    "properties": {
                        "entities": {"type": "array"},
                        "questions": {"type": "array"}
                    },
                    "required": ["entities", "questions"]
                }
            )
        ]

        result = self.service.run_chain(self.session_id, chain)

        if result:
            callback(result[0])