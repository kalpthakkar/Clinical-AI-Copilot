import json
import os
from datetime import timezone, datetime


class ClinicalStateManager:

    def __init__(self, file_path="clinical_state.json"):
        self.file_path = file_path

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f)

    # -------------------------
    # Convert non-serializable objects
    # -------------------------
    def _serialize(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}

        if isinstance(obj, list):
            return [self._serialize(v) for v in obj]

        return obj

    # -------------------------
    # Update state
    # -------------------------
    def update(self, data):

        # 🔥 Convert everything safely
        safe_data = self._serialize(data)

        # Handle corrupted file case
        try:
            with open(self.file_path, "r") as f:
                state = json.load(f)
        except Exception:
            state = {}

        state[str(datetime.now(timezone.utc).isoformat())] = safe_data

        with open(self.file_path, "w") as f:
            json.dump(state, f, indent=2)