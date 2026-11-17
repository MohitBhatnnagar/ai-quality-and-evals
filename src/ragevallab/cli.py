from __future__ import annotations

import argparse
import sys

from .evaluate import compare, load_corpus, load_golden, render


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ragevallab", description="Compare retrievers on a golden set")
    p.add_argument("docs", help="directory of .txt documents")
    p.add_argument("golden", help="golden set JSON: [{question, relevant: [file.txt]}]")
    p.add_argument("-k", type=int, default=3)
    p.add_argument("--chunk-words", type=int, default=40)
    a = p.parse_args(argv)
    print(render(compare(load_corpus(a.docs, a.chunk_words), load_golden(a.golden), a.k)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
