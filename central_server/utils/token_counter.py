def estimate_tokens(text: str) -> int:
    # simple approximation: 1 token ≈ 4 chars
    return max(1, len(text) // 4)