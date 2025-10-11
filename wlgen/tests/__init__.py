import filecmp
import unittest
import os
import wlgen


class wlgen_test(unittest.TestCase):
    def setUp(self):
        self.cset = {0: "123", 1: "ABC", 2: ' !"$'}
        if os.name == "nt":
            self.sample = "wlgen/tests/files/sample_mixed_dos"
        else:
            self.sample = "wlgen/tests/files/sample_mixed_unix"

    def test_mixed_words(self):
        tfilepath = "wlgen/tests/files/tmp"
        with open(tfilepath, "w", encoding="utf-8") as tfile:
            for word in wlgen.gen_words(self.cset):
                tfile.write("%s\n" % word)
        self.assertTrue(filecmp.cmp(tfilepath, self.sample))

    def test_mixed_list(self):
        tfilepath = "wlgen/tests/files/tmp"
        with open(tfilepath, "w", encoding="utf-8") as tfile:
            for word in wlgen.gen_wordlist(self.cset):
                tfile.write("%s\n" % word)
        self.assertTrue(filecmp.cmp(tfilepath, self.sample))

    def test_mixed_iter(self):
        tfilepath = "wlgen/tests/files/tmp"
        with open(tfilepath, "w", encoding="utf-8") as tfile:
            for word in wlgen.gen_wordlist_iter(self.cset):
                tfile.write("%s\n" % word)
        self.assertTrue(filecmp.cmp(tfilepath, self.sample))

    def test_clean_input_false(self):
        """Test gen_wordlist_iter with clean_input=False (default behavior)"""
        # Test with unsorted/duplicate input
        dirty_cset = {0: "321", 1: "CBAA", 2: '$" !"'}
        result_default = list(wlgen.gen_wordlist_iter(dirty_cset))
        result_clean_false = list(wlgen.gen_wordlist_iter(dirty_cset, clean_input=False))
        # Both should produce identical sorted output
        self.assertEqual(result_default, result_clean_false)

    def test_clean_input_true(self):
        """Test gen_wordlist_iter with clean_input=True skips preprocessing"""
        # Test with already sorted/unique input
        clean_cset = {0: "123", 1: "ABC"}
        result_default = list(wlgen.gen_wordlist_iter(clean_cset))
        result_clean_true = list(wlgen.gen_wordlist_iter(clean_cset, clean_input=True))
        # Both should produce identical output when input is already clean
        self.assertEqual(result_default, result_clean_true)

    def test_clean_input_produces_same_output(self):
        """Test that both code paths produce identical output for clean input"""
        result_cleaned = list(wlgen.gen_wordlist_iter(self.cset, clean_input=False))
        result_raw = list(wlgen.gen_wordlist_iter(self.cset, clean_input=True))
        # Should produce same output since self.cset is already clean
        self.assertEqual(result_cleaned, result_raw)


class TestSmartDispatcher(unittest.TestCase):
    """Tests for estimate_wordlist_size and generate_wordlist dispatcher"""

    def test_estimate_size_simple(self):
        """Test size estimation with simple charsets"""
        self.assertEqual(wlgen.estimate_wordlist_size({0: '123', 1: 'AB'}), 6)
        self.assertEqual(wlgen.estimate_wordlist_size({0: 'abc', 1: 'xyz', 2: '123'}), 27)

    def test_estimate_size_empty(self):
        """Test size estimation with empty charset"""
        self.assertEqual(wlgen.estimate_wordlist_size({}), 0)

    def test_estimate_size_duplicates(self):
        """Test size estimation handles duplicate characters"""
        # '111' should be treated as '1' (1 unique char)
        self.assertEqual(wlgen.estimate_wordlist_size({0: '111', 1: 'AB'}), 2)
        # 'AAA' should be treated as 'A' (1 unique char)
        self.assertEqual(wlgen.estimate_wordlist_size({0: '123', 1: 'AAA'}), 3)

    def test_estimate_size_large(self):
        """Test size estimation with larger charsets"""
        # 5 positions, 10 chars each = 100,000
        charset = {i: '0123456789' for i in range(5)}
        self.assertEqual(wlgen.estimate_wordlist_size(charset), 100000)

    def test_dispatcher_auto_tiny(self):
        """Test dispatcher selects gen_wordlist for tiny problems (<1K)"""
        # 3*3*3 = 27 combinations (tiny)
        charset = {0: '123', 1: 'abc', 2: 'xyz'}
        result = wlgen.generate_wordlist(charset, method='auto')
        # Should return a list (from gen_wordlist)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 27)

    def test_dispatcher_auto_small(self):
        """Test dispatcher selects gen_wordlist for small problems (1K-100K)"""
        # 5*5*5*5 = 625 combinations (tiny)
        charset = {i: '12345' for i in range(4)}
        result = wlgen.generate_wordlist(charset, method='auto')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 625)

    def test_dispatcher_auto_medium(self):
        """Test dispatcher selects gen_wordlist_iter for medium problems (100K+)"""
        # 10*10*10*10*10 = 100,000 combinations (medium)
        charset = {i: '0123456789' for i in range(5)}
        result = wlgen.generate_wordlist(charset, method='auto')
        # Should return an iterator (from gen_wordlist_iter)
        self.assertFalse(isinstance(result, list))
        # Consume iterator and verify count
        count = sum(1 for _ in result)
        self.assertEqual(count, 100000)

    def test_dispatcher_prefer_memory_efficient(self):
        """Test prefer_memory_efficient forces generator for all sizes"""
        # Tiny problem (27 combinations)
        charset = {0: '123', 1: 'abc', 2: 'xyz'}
        result = wlgen.generate_wordlist(charset, method='auto', prefer_memory_efficient=True)
        # Should return iterator even for tiny problem
        self.assertFalse(isinstance(result, list))
        self.assertEqual(sum(1 for _ in result), 27)

    def test_dispatcher_manual_list(self):
        """Test manual method='list' selection"""
        charset = {0: '123', 1: 'AB'}
        result = wlgen.generate_wordlist(charset, method='list')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 6)

    def test_dispatcher_manual_iter(self):
        """Test manual method='iter' selection"""
        charset = {0: '123', 1: 'AB'}
        result = wlgen.generate_wordlist(charset, method='iter')
        self.assertFalse(isinstance(result, list))
        self.assertEqual(sum(1 for _ in result), 6)

    def test_dispatcher_manual_words(self):
        """Test manual method='words' selection"""
        charset = {0: '123', 1: 'AB'}
        result = wlgen.generate_wordlist(charset, method='words')
        self.assertFalse(isinstance(result, list))
        self.assertEqual(sum(1 for _ in result), 6)

    def test_dispatcher_clean_input_passthrough(self):
        """Test clean_input parameter is passed through to gen_wordlist_iter"""
        charset = {0: '123', 1: 'ABC'}
        # Both should produce identical results for clean input
        result_default = list(wlgen.generate_wordlist(charset, method='iter', clean_input=False))
        result_clean = list(wlgen.generate_wordlist(charset, method='iter', clean_input=True))
        self.assertEqual(result_default, result_clean)

    def test_dispatcher_invalid_method(self):
        """Test dispatcher raises error for invalid method"""
        charset = {0: '123'}
        with self.assertRaises(ValueError) as context:
            wlgen.generate_wordlist(charset, method='invalid')
        self.assertIn("Invalid method", str(context.exception))

    def test_dispatcher_correctness(self):
        """Test dispatcher produces correct output matching other implementations"""
        charset = {0: '12', 1: 'AB', 2: 'xy'}
        expected = list(wlgen.gen_wordlist_iter(charset))

        # Test all auto-selected methods produce same output
        result_auto = list(wlgen.generate_wordlist(charset, method='auto'))
        result_list = wlgen.generate_wordlist(charset, method='list')
        result_iter = list(wlgen.generate_wordlist(charset, method='iter'))
        result_words = list(wlgen.generate_wordlist(charset, method='words'))

        self.assertEqual(result_auto, expected)
        self.assertEqual(result_list, expected)
        self.assertEqual(result_iter, expected)
        self.assertEqual(result_words, expected)


if __name__ == "__main__":
    unittest.main()
