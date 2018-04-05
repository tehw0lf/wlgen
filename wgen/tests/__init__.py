import filecmp
import unittest
import os
import wgen


class wgen_test(unittest.TestCase):
    def setUp(self):
        self.cset = {0: '123', 1: 'ABC', 2: '!"§ '}
        if os.name == 'nt':
            self.sample = 'wgen/tests/files/sample_mixed_dos.lst'
        else:
            self.sample = 'wgen/tests/files/sample_mixed_unix.lst'

    def test_mixed_words(self):
        tfilepath = 'wgen/tests/files/tmp'
        with open(tfilepath, 'w', encoding='utf-8') as tfile:
            for word in wgen.gen_words(self.cset):
                tfile.write('%s\n' % word)
        self.assertTrue(filecmp.cmp(tfilepath, self.sample))

    def test_mixed_list(self):
        tfilepath = 'wgen/tests/files/tmp'
        with open(tfilepath, 'w', encoding='utf-8') as tfile:
            for word in wgen.gen_words(self.cset):
                tfile.write('%s\n' % word)
        self.assertTrue(filecmp.cmp(tfilepath, self.sample))
