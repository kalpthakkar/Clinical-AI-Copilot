import json
import math
from pathlib import Path
from central_server.config.env_config import EMBEDDINGS_PATH

# ----------------- CONFIG -----------------
MIN_THRESHOLD = 0.75
MAX_THRESHOLD = 0.95
SINGLE_WORD_MIN_THRESHOLD = 0.80


# ----------------------- UTILS -----------------------------

def cosine_normalized(a, b):
    """Dot product (assumes normalized embeddings)"""
    return sum(x * y for x, y in zip(a, b))


def mean(arr):
    return sum(arr) / len(arr) if arr else 0


def std(arr):
    if not arr:
        return 0
    m = mean(arr)
    variance = sum((x - m) ** 2 for x in arr) / len(arr)
    return math.sqrt(variance)


def num_words(label):
    return len(label.strip().split())


def clamp(val, min_val, max_val):
    return min(max_val, max(min_val, val))


# ------------------- THRESHOLD CALCULATION --------------------------

def compute_thresholds_for_group_superior(labels):
    if not labels:
        return

    if len(labels) == 1:
        labels[0]["threshold"] = clamp(0.9, MIN_THRESHOLD, MAX_THRESHOLD)
        return

    # --- 1️⃣ Pairwise similarities ---
    sims_matrix = [[] for _ in labels]
    all_sims = []

    for i in range(len(labels)):
        a = labels[i]["embedding"]
        for j in range(len(labels)):
            if i == j:
                continue
            b = labels[j]["embedding"]
            sim = cosine_normalized(a, b)
            sims_matrix[i].append(sim)
            all_sims.append(sim)

    # --- 2️⃣ Group stats ---
    group_mean = mean(all_sims)
    group_std = std(all_sims)

    sorted_sims = sorted(all_sims)
    p90_index = int(0.9 * len(sorted_sims))
    percentile90 = sorted_sims[p90_index] if sorted_sims else 0.95

    max_threshold_for_group = clamp(percentile90, MIN_THRESHOLD, MAX_THRESHOLD)

    # --- 3️⃣ Per-label thresholds ---
    for i, label in enumerate(labels):
        sim_values = sims_matrix[i]

        base = mean(sim_values) - 0.5 * std(sim_values)

        # deviation from group
        label_mean = mean(sim_values)
        deviation_from_group = label_mean - group_mean
        base += deviation_from_group * 0.3

        # length adjustment
        word_count = num_words(label["text"])
        length_factor = 1 + min(0.03 * word_count, 0.10)
        base *= length_factor

        # safeguards
        if word_count == 1:
            base = max(base, SINGLE_WORD_MIN_THRESHOLD)

        if word_count > 7 and base < 0.85:
            base = 0.85

        base = clamp(base, MIN_THRESHOLD, max_threshold_for_group)

        label["threshold"] = round(base, 3)


# ------------------- MAIN SCRIPT --------------------------

def generate_thresholds():
    print("[THRESHOLDS] Loading label embeddings...")

    with open(EMBEDDINGS_PATH, "r") as f:
        data = json.load(f)

    if "questions" not in data:
        print("[THRESHOLDS] No questions found.")
        return

    print("[THRESHOLDS] Computing thresholds...")

    for group_key, group in data["questions"].items():
        labels = group.get("labels", [])

        if not labels:
            continue

        if len(labels) == 1:
            labels[0]["threshold"] = clamp(0.9, MIN_THRESHOLD, MAX_THRESHOLD)
            continue

        compute_thresholds_for_group_superior(labels)

    # Save
    with open(EMBEDDINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print("[THRESHOLDS] Done ✅")


# ------------------- RUN --------------------------

if __name__ == "__main__":
    generate_thresholds()