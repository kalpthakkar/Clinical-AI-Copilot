from typing import Dict, List, Literal, Optional

from central_server.nlp.entity_extractor import EntityExtractor
from central_server.rag.question_detector import QuestionDetector
from central_server.nlp.ontology_mapper import OntologyMapper
from central_server.nlp.llm_summarizer import LLMSummarizer
from central_server.nlp.sentencizer import SentenceSplitter
from central_server.memory.clinical_state_manager import ClinicalStateManager
from central_server.conversation.state_engine import ConversationStateEngine


class TranscriptionPipeline:

    def __init__(self):

        self.entity_extractor = EntityExtractor()
        self.question_detector = QuestionDetector()
        self.ontology_mapper = OntologyMapper()
        self.llm = LLMSummarizer()
        self.sentence_splitter = SentenceSplitter()
        self.state_manager = ClinicalStateManager()
        self.conv_engine = ConversationStateEngine(max_history=3)

    # ----------------------------------
    # Main processing
    # ----------------------------------
    def process_event(self, event):

        text = event.transcript

        # -------------------------
        # 1. Update conversation memory
        # -------------------------
        self.conv_engine.add_event(event)

        # -------------------------
        # 2. Detect questions (doctor only)
        # -------------------------
        if event.speaker == "doctor":
            sentences = self.sentence_splitter.split(text)
            for sentence in sentences:
                detected_question: Optional[Dict[Literal['question_id', 'question', 'match_score'], str | float]] = self.question_detector.detect(input_text=sentence, full_scan=False)
                if detected_question:
                    print("🌟 Detected Question:::", detected_question)
                    self.conv_engine.register_question(detected_question['question_id'], event)

        # -------------------------
        # 3. Resolve answers (patient only)
        # -------------------------
        resolved_pairs = self.conv_engine.resolve_answers(event)

        structured_answers = []

        for pair in resolved_pairs:

            q_id = pair["question_id"]

            enum_value, confidence = self.ontology_mapper.map_answer(
                q_id, pair["answer"]
            )

            summary = self.llm.summarize(pair["answer"])

            structured_answers.append({
                "question_id": q_id,
                "question": pair["question"],
                "raw_answer": pair["answer"],
                "normalized_answer": enum_value,
                "summary": summary,
                "confidence": confidence,
                "question_time": str(pair["question_time"]),
                "answer_time": str(pair["answer_time"])
            })

        # -------------------------
        # 4. Entity extraction (always)
        # -------------------------
        entities = self.entity_extractor.extract(text)

        # -------------------------
        # 5. Build output bundle
        # -------------------------
        bundle = {
            "speaker": event.speaker,
            "timestamp_start": str(event.timestamp_start),
            "timestamp_end": str(event.timestamp_end),
            "text": text,
            "entities": entities,
            "structured_answers": structured_answers,
            "context_window": self.conv_engine.get_context()
        }

        # -------------------------
        # 6. Persist
        # -------------------------
        self.state_manager.update(bundle)

        return bundle