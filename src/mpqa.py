"""
Some utilities for the MPQA subjectivity clues lexicon.
Author: Kyle Hardgrave (kyleh@seas)
"""

import os
from collections import namedtuple, defaultdict


# The root MPQA file
LEXICON_FILE = ('/project/cis/nlp/data/corpora/mpqa-lexicon/'
                'subjclueslen1-HLTEMNLP05.tff')

# The MPQA keys for word data
WORD_KEY = 'word1'
POL_KEY = 'priorpolarity'
TYPE_KEY = 'type'

# The MPQA tokens for a word's polarity
POL_TOKS = {
  'pos': 'positive',
  'neg': 'negative',
  'neut': 'neutral',
  'both': 'both',
  }

# The MPQA tokens for a word's sentiment type (strength)
TYPE_TOKS = {
  'strong': 'strongsubj',
  'weak': 'weaksubj',
  }


# A class for accessing MPQA word data
MpqaWord = namedtuple('MpqaWord', ['word', 'strength', 'polarity'])


def get_word_sentiment_map(lexicon_file=LEXICON_FILE):
  """Return a dictionary from words to list of MpqaWord named tuples.

  TODO: Fix doctest
  >> get_mpqa_lexicon()['best']
  [('strongsubj', 'positive')]
  >> get_mpqa_lexicon()['mean']
  [('strongsubj', 'negative'), ('weaksubj', 'neutral')]
  """
  results = defaultdict(list)
  with open(lexicon_file, 'r') as f:
    for line in f:
      data = parse_line(line)
      results[data.word].append(data)
  return dict(results)


def parse_line(line):
  """Parse a line of the lexicon file into an MpqaWord named tuple."""
  data = {}
  for pair in line.strip().split():
    try:
      key, val = pair.split('=')
      data[key] = val
    except ValueError: # Occasional errant string
      continue
  return MpqaWord(data[WORD_KEY], data[TYPE_KEY], data[POL_KEY])
