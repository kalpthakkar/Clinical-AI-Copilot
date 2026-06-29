import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict

env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

# 🔗 Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVER_ROOT = Path(__file__).resolve().parents[1]

# =========================
# ...
# =========================
# ---------------
# ...
# ---------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "mxbai-embed-large:latest")

EMBEDDINGS_FILENAME = "question_embeddings.json"
EMBEDDINGS_PATH = PROJECT_ROOT / "central_server" / "rag" / EMBEDDINGS_FILENAME