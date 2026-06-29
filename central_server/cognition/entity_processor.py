from central_server.cognition.entity_store import EntityStore


class EntityProcessor:

    def __init__(self):
        self.store = EntityStore()

    # ----------------------------------
    # Main entry
    # ----------------------------------
    def process(self, extracted_entities):

        if not extracted_entities:
            return []

        processed = []

        for entity in extracted_entities:

            normalized = self._normalize(entity)

            if not normalized:
                continue

            self.store.upsert(normalized)
            processed.append(normalized)

        return processed

    # ----------------------------------
    # Normalize entity
    # ----------------------------------
    def _normalize(self, entity):

        if "value" not in entity or not entity["value"]:
            return None

        return {
            "type": entity.get("type", "").lower(),
            "value": entity.get("value", "").lower(),
            "tooth_location": entity.get("tooth_location"),
            "time": entity.get("time"),
            "speaker": entity.get("speaker")
        }