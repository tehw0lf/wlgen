import filecmp
import unittest
import wgen


class wgen_test(unittest.TestCase):
    def test_3digits(self):
        cset = {0: '123456789', 1: '123456789', 2: '123456789'}
        sample = 'wgen/tests/files/sample_3digits.lst'
        tfilepath = 'wgen/tests/files/tmp'
        with open(tfilepath, 'w') as tfile:
            for word in wgen.gen_wordlist(cset):
                tfile.write('%s\n' % word)
        self.assertTrue(filecmp.cmp(tfilepath, sample))
