"""Tokenisation and chunking."""
from __future__ import annotations

import re

STOP = frozenset("a an and are as at be by for from has have in is it of on or that the to was were will with".split())
_WORD = re.compile(r"[a-z0-9]+")


def tokenize(text: str, drop_stop: bool = True) -> list[str]:
    toks = _WORD.findall(text.lower())
    return [t for t in toks if t not in STOP] if drop_stop else toks


def chunk_fixed(text: str, size: int = 60, overlap: int = 10) -> list[str]:
    """Word windows of `size` with `overlap` words shared between neighbours."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("need size > 0 and 0 <= overlap < size")
    words = text.split()
    if not words:
        return []
    step = size - overlap
    out = []
    for start in range(0, len(words), step):
        out.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
    return out


def chunk_sentences(text: str, max_words: int = 60) -> list[str]:
    """Pack whole sentences into chunks up to `max_words`; never splits a sentence."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    chunks, cur, n = [], [], 0
    for s in sentences:
        w = len(s.split())
        if cur and n + w > max_words:
            chunks.append(" ".join(cur))
            cur, n = [], 0
        cur.append(s)
        n += w
    if cur:
        chunks.append(" ".join(cur))
    return chunks
