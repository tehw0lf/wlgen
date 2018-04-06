[![Build Status](https://travis-ci.org/tehw0lf/wlgen.svg?branch=master)](https://travis-ci.org/tehw0lf/wlgen) [![codecov](https://codecov.io/gh/tehw0lf/wlgen/branch/master/graph/badge.svg)](https://codecov.io/gh/tehw0lf/wlgen)

# Description
A recursive wordlist generator written in Python.
For each string position, custom character sets can be defined.

# Prerequisites
Python 3.x (developed on Python 3.6.4)

# Instructions
## Installation
To install from GitHub:
```
git clone https://github.com/tehw0lf/wlgen.git
cd wlgen
python setup.py test (optional unit tests to ensure functionality)
pip install .
```

To install from PyPI:
```
pip install wlgen
```

## Which function should I use?
Currently there are two implementations to generate a wordlist.
`gen_wordlist` builds the whole list in memory before writing it, `gen_words` is a generator that is memory efficient but slower.