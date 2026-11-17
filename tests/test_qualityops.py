import unittest

from qualityops import (cohens_kappa, dpmo, first_pass_yield, interpret, needs_recalibration,
                        out_of_control, p_chart, pairwise_kappa, pareto, sigma_level,
                        strictness, vital_few)


class MetricTests(unittest.TestCase):
    def test_first_pass_yield(self):
        self.assertAlmostEqual(first_pass_yield(95, 100), 0.95)

    def test_first_pass_yield_validates(self):
        with self.assertRaises(ValueError):
            first_pass_yield(5, 0)
        with self.assertRaises(ValueError):
            first_pass_yield(11, 10)

    def test_dpmo(self):
        self.assertEqual(dpmo(30, 1000, 10), 3000.0)

    def test_sigma_known_value(self):
        # 66,807 DPMO is the textbook 3-sigma process with the 1.5 shift
        self.assertAlmostEqual(sigma_level(66807), 3.0, places=2)
        self.assertAlmostEqual(sigma_level(3.4), 6.0, places=1)

    def test_pareto_and_vital_few(self):
        causes = ["brief"] * 6 + ["template"] * 3 + ["typo"] * 1 + [""]
        p = pareto(causes)
        self.assertEqual([c for c, _, _ in p], ["brief", "template", "typo"])
        self.assertAlmostEqual(p[-1][2], 1.0)
        self.assertEqual(vital_few(causes, 0.8), ["brief", "template"])


class SpcTests(unittest.TestCase):
    def test_stable_process_has_no_signals(self):
        d = [5, 6, 4, 5, 6, 5, 4, 6, 5, 5]
        _, pts = p_chart(d, [100] * len(d))
        self.assertEqual(out_of_control(pts), [])

    def test_spike_above_ucl(self):
        d = [5] * 10 + [30]
        _, pts = p_chart(d, [100] * 11)
        self.assertIn("above UCL", pts[-1].signals)

    def test_shift_detected(self):
        d = [5, 4, 6, 5, 4, 6, 5, 5] + [9, 9, 9, 9, 9, 9, 9, 9]
        _, pts = p_chart(d, [100] * 16)
        self.assertTrue(any("8 in a row" in s for p in pts for s in p.signals))

    def test_trend_detected(self):
        d = [4, 5, 6, 7, 8, 9]
        _, pts = p_chart(d, [100] * 6)
        self.assertIn("6-point trend", pts[-1].signals)

    def test_variable_subgroup_sizes_change_limits(self):
        _, pts = p_chart([5, 50], [100, 1000])
        self.assertLess(pts[1].ucl - pts[1].lcl, pts[0].ucl - pts[0].lcl)

    def test_invalid_data(self):
        with self.assertRaises(ValueError):
            p_chart([5], [3])


class CalibrationTests(unittest.TestCase):
    def test_perfect_agreement(self):
        a = ["pass", "fail", "pass", "fail"]
        self.assertAlmostEqual(cohens_kappa(a, a), 1.0)

    def test_chance_agreement_is_zero(self):
        a = ["pass", "pass", "fail", "fail"]
        b = ["pass", "fail", "pass", "fail"]
        self.assertAlmostEqual(cohens_kappa(a, b), 0.0)

    def test_kappa_punishes_skewed_agreement(self):
        a = ["pass"] * 9 + ["fail"]
        b = ["pass"] * 8 + ["fail", "pass"]
        self.assertGreater(sum(x == y for x, y in zip(a, b)) / 10, 0.7)  # 80% raw agreement
        self.assertLess(cohens_kappa(a, b), 0.0)                          # but worse than chance

    def test_interpret_bands(self):
        self.assertEqual(interpret(-0.1), "no better than chance")
        self.assertEqual(interpret(0.55), "moderate")
        self.assertEqual(interpret(0.9), "almost perfect")

    def test_recalibration_flags_the_outlier(self):
        base = ["pass", "fail", "pass", "pass", "fail", "pass", "fail", "pass"]
        harsh = ["fail"] * 8
        ratings = {"r1": base, "r2": list(base), "r3": list(base), "r4": harsh}
        self.assertEqual(needs_recalibration(ratings), ["r4"])
        z = strictness(ratings)
        self.assertGreater(z["r4"], 1.0)

    def test_needs_three_reviewers(self):
        with self.assertRaises(ValueError):
            needs_recalibration({"a": ["pass"], "b": ["pass"]})

    def test_pairwise_keys(self):
        r = {"a": ["pass", "fail"], "b": ["pass", "fail"], "c": ["fail", "pass"]}
        self.assertEqual(set(pairwise_kappa(r)), {("a", "b"), ("a", "c"), ("b", "c")})


if __name__ == "__main__":
    unittest.main()
