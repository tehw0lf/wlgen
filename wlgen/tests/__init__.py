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


if __name__ == "__main__":
    unittest.main()
