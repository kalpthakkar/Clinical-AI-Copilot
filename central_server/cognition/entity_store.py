import uuid
import json
import os
from datetime import datetime


class EntityStore:

    def __init__(self, file_path="entity_extraction.json"):
        self.file_path = file_path
        self.entities = []

        self._load()

    # ----------------------------------
    # Load existing data
    # ----------------------------------
    def _load(self):

        if not os.path.exists(self.file_path):
            self._save()
            return

        try:
            with open(self.file_path, "r") as f:
                self.entities = json.load(f)
        except Exception:
            print("⚠️ Corrupted entity file. Resetting...")
            self.entities = []
            self._save()

    # ----------------------------------
    # Save safely
    # ----------------------------------
    def _save(self):

        tmp_file = self.file_path + ".tmp"

        with open(tmp_file, "w") as f:
            json.dump(self.entities, f, indent=2)

        os.replace(tmp_file, self.file_path)

    # ----------------------------------
    # Add or update entity
    # ----------------------------------
    def upsert(self, entity):

        match = self._find_match(entity)

        if match:
            self._merge(match, entity)
        else:
            entity["id"] = str(uuid.uuid4())
            entity["created_at"] = datetime.utcnow().isoformat()
            entity["mentions"] = []

            self.entities.append(entity)

        # 🔥 persist after every update
        self._save()

    # ----------------------------------
    # Find similar entity
    # ----------------------------------
    def _find_match(self, new_entity):

        for e in self.entities:

            if e["type"] != new_entity["type"]:
                continue

            if e["value"].lower() == new_entity["value"].lower():
                return e

        return None

    # ----------------------------------
    # Merge logic
    # ----------------------------------
    def _merge(self, existing, new):

        for key in ["tooth_location", "time"]:

            if not existing.get(key) and new.get(key):
                existing[key] = new[key]

        existing.setdefault("mentions", []).append({
            "time": new.get("time"),
            "speaker": new.get("speaker"),
            "updated_at": datetime.utcnow().isoformat()
        })

        existing["last_updated"] = datetime.utcnow().isoformat()

    # ----------------------------------
    # Debug
    # ----------------------------------
    def get_all(self):
        return self.entities