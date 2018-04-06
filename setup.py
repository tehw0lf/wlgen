from setuptools import setup

setup(name='wgen',
      version='1.0',
      description='A recursive wordlist generator written in python',
      long_description='''A recursive wordlist generator written in Python.
For each string position, custom character sets can be defined.
Currently there are two implementations to generate a wordlist.
gen_wordlist builds the whole list in memory before writing it,
gen_words is a generator that is memory efficient but slower.
''',
      url='https://github.com/tehw0lf/wgen',
      author='tehw0lf',
      author_email='tehwolf@protonmail.com',
      license='MIT',
      packages=['wgen'],
      zip_safe=False
      )
