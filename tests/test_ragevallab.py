import math
import os
import unittest

from ragevallab import (BM25, Hybrid, TfIdf, bootstrap_ci, chunk_fixed, chunk_sentences, compare, doc_of,
                        hit_at_k, load_corpus, load_golden, ndcg_at_k, paired_bootstrap_diff,
                        recall_at_k, reciprocal_rank, tokenize)

HERE = os.path.dirname(__file__)
EX = os.path.join(HERE, "..", "examples")
CORPUS = [("a", "apples and oranges are fruit"), ("b", "cars and trucks are vehicles"),
          ("c", "bananas are yellow fruit")]


class TextTests(unittest.TestCase):
    def test_tokenize_drops_stopwords(self):
        self.assertEqual(tokenize("The cat is on the mat"), ["cat", "mat"])

    def test_fixed_chunks_overlap(self):
        c = chunk_fixed("a b c d e f g h", size=4, overlap=2)
        self.assertEqual(c, ["a b c d", "c d e f", "e f g h"])

    def test_fixed_chunk_validates(self):
        with self.assertRaises(ValueError):
            chunk_fixed("a b", size=2, overlap=2)

    def test_sentence_chunks_never_split_sentence(self):
        c = chunk_sentences("One two three. Four five six. Seven eight.", max_words=6)
        self.assertEqual(c, ["One two three. Four five six.", "Seven eight."])


class MetricTests(unittest.TestCase):
    def test_hit_recall_rr(self):
        r = ["x", "a", "y"]
        self.assertEqual(hit_at_k(r, {"a"}, 1), 0.0)
        self.assertEqual(hit_at_k(r, {"a"}, 2), 1.0)
        self.assertEqual(recall_at_k(r, {"a", "z"}, 3), 0.5)
        self.assertEqual(reciprocal_rank(r, {"a"}), 0.5)
        self.assertEqual(reciprocal_rank(r, {"q"}), 0.0)

    def test_ndcg_perfect_and_worse(self):
        self.assertAlmostEqual(ndcg_at_k(["a", "b"], {"a", "b"}, 2), 1.0)
        self.assertLess(ndcg_at_k(["x", "a"], {"a"}, 2), 1.0)
        self.assertAlmostEqual(ndcg_at_k(["x", "a"], {"a"}, 2), 1 / math.log2(3))

    def test_bootstrap_ci_brackets_mean(self):
        v = [0.0, 1.0] * 20
        lo, hi = bootstrap_ci(v)
        self.assertTrue(lo < 0.5 < hi)

    def test_paired_diff_detects_real_gap(self):
        a, b = [1.0] * 30, [0.0] * 30
        d, lo, hi = paired_bootstrap_diff(a, b)
        self.assertEqual((d, lo, hi), (1.0, 1.0, 1.0))

    def test_paired_diff_no_gap_spans_zero(self):
        a = [1.0, 0.0] * 20
        b = [0.0, 1.0] * 20
        _, lo, hi = paired_bootstrap_diff(a, b)
        self.assertLessEqual(lo, 0.0)
        self.assertGreaterEqual(hi, 0.0)

    def test_paired_requires_equal_length(self):
        with self.assertRaises(ValueError):
            paired_bootstrap_diff([1.0], [1.0, 2.0])


class RetrieverTests(unittest.TestCase):
    def test_bm25_ranks_relevant_first(self):
        self.assertEqual(BM25(CORPUS).search("yellow bananas")[0], "c")

    def test_tfidf_ranks_relevant_first(self):
        self.assertEqual(TfIdf(CORPUS).search("trucks vehicles")[0], "b")

    def test_no_match_returns_empty(self):
        self.assertEqual(BM25(CORPUS).search("quantum chromodynamics"), [])

    def test_hybrid_fuses_both(self):
        h = Hybrid([BM25(CORPUS), TfIdf(CORPUS)])
        self.assertEqual(h.search("fruit bananas")[0], "c")

    def test_doc_of(self):
        self.assertEqual(doc_of("policy.txt#3"), "policy.txt")


class EndToEndTests(unittest.TestCase):
    def test_sample_run_is_sensible_and_deterministic(self):
        corpus = load_corpus(os.path.join(EX, "docs"))
        golden = load_golden(os.path.join(EX, "golden.json"))
        r1, r2 = compare(corpus, golden, k=3), compare(corpus, golden, k=3)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["queries"], 14)
        for s in r1["summary"].values():
            self.assertGreaterEqual(s["hit@k"], 0.5)


if __name__ == "__main__":
    unittest.main()
