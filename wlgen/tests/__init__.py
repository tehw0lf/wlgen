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

    def test_mixed_numpy(self):
        """Test gen_wordlist_numpy produces identical output to other implementations"""
        if not wlgen.HAS_NUMPY:
            self.skipTest("NumPy not available")

        tfilepath = "wlgen/tests/files/tmp"
        with open(tfilepath, "w", encoding="utf-8") as tfile:
            for word in wlgen.gen_wordlist_numpy(self.cset):
                tfile.write("%s\n" % word)
        self.assertTrue(filecmp.cmp(tfilepath, self.sample))

    def test_numpy_clean_input_false(self):
        """Test gen_wordlist_numpy with clean_input=False (default behavior)"""
        if not wlgen.HAS_NUMPY:
            self.skipTest("NumPy not available")

        # Test with unsorted/duplicate input
        dirty_cset = {0: "321", 1: "CBAA", 2: '$" !"'}
        result_default = list(wlgen.gen_wordlist_numpy(dirty_cset))
        result_clean_false = list(wlgen.gen_wordlist_numpy(dirty_cset, clean_input=False))
        # Both should produce identical sorted output
        self.assertEqual(result_default, result_clean_false)

    def test_numpy_clean_input_true(self):
        """Test gen_wordlist_numpy with clean_input=True skips preprocessing"""
        if not wlgen.HAS_NUMPY:
            self.skipTest("NumPy not available")

        # Test with already sorted/unique input
        clean_cset = {0: "123", 1: "ABC"}
        result_default = list(wlgen.gen_wordlist_numpy(clean_cset))
        result_clean_true = list(wlgen.gen_wordlist_numpy(clean_cset, clean_input=True))
        # Both should produce identical output when input is already clean
        self.assertEqual(result_default, result_clean_true)

    def test_numpy_produces_same_output(self):
        """Test that NumPy implementation produces identical output to itertools"""
        if not wlgen.HAS_NUMPY:
            self.skipTest("NumPy not available")

        result_iter = list(wlgen.gen_wordlist_iter(self.cset))
        result_numpy = list(wlgen.gen_wordlist_numpy(self.cset))
        # Should produce identical output
        self.assertEqual(result_iter, result_numpy)

    def test_numpy_import_error(self):
        """Test that gen_wordlist_numpy raises ImportError when NumPy unavailable"""
        if wlgen.HAS_NUMPY:
            self.skipTest("NumPy is available")

        with self.assertRaises(ImportError):
            list(wlgen.gen_wordlist_numpy(self.cset))


if __name__ == "__main__":
    unittest.main()
