"""
A parser for the MPQA subjectivity clues lexicon.
Author: Kyle Hardgrave (kyleh@seas)
"""
import os



LEXICON_ROOT = ('/project/cis/nlp/data/corpora/mpqa-lexicon/'
                'subjclueslen1-HLTEMNLP05.tff')
# The MPQA tokens for a word's polarity
POL_TOK = {
  'pos' = 'positive',
  'neg' = 'negative',
  'neut' = 'neutral',
  'both' = 'both',
  }

# The MPQA tokens for a word's sentiment type (strength)
TYPE_TOK = {
  'strong' = 'strongsubj',
  'weak' = 'weaksubj',
  }


def mpqa_data(from_file=LEXICON_ROOT):
  """Return a dictionary from words to list of tuples of
  (word_type, sentiment).

  >>> get_mpqa_lexicon()['best']
  [('strongsubj', 'positive')]
  >>> get_mpqa_lexicon()['mean']
  [('strongsubj', 'negative'), ('weaksubj', 'neutral')]
  """
  results = defaultdict(list)
  with open(lexicon_path, 'r') as f:
    for line in f:
      data = parse_line(line)
      results[data['word1']].append((data['type'], data['priorpolarity']))
  return results


def parse_line(line):
  """Parse a line of the lexicon file into a dict of its data."""
  data = {}
  for pair in line.strip().split():
    try:
      key, val = pair.split('=')
      data[key] = val
    except ValueError: # Occasional errant string
      continue
  return data
